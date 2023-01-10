import hashlib

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


def img_path(instance, filename):
    ext = filename.rsplit('.')[-1]
    return 'img/{}.{}'.format(instance.pk, ext)


class Board(models.Model):
    # info
    name = models.CharField(max_length=16)
    ln = models.SlugField(max_length=8)
    description = models.TextField(blank=True)
    # settings
    max_threads = models.IntegerField(null=True, default=100)
    thread_bump_limit = models.IntegerField(null=True, default=500)
    thread_img_limit = models.IntegerField(null=True, default=150)
    archive_retention_time = models.TimeField(null=True)
    op_requires_img = models.BooleanField(default=False)
    textboard = models.BooleanField(default=False)

    def __str__(self):
        return self.ln

    def get_absolute_url(self):
        return reverse('board', kwargs={'board': self.ln})


class Post(models.Model):
    # server generated
    board = models.ForeignKey(
        'Board', on_delete=models.CASCADE, null=False, blank=False)
    thread = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    bump = models.DateTimeField(null=True)
    closed = models.BooleanField(default=False)
    cookie = models.CharField(max_length=32, blank=True)
    # user provided
    author = models.CharField(max_length=32, default='Anonymous')
    tripcode = models.CharField(max_length=10, blank=True)
    subject = models.CharField(max_length=64, blank=True)
    text = models.TextField(blank=True)
    image = models.ImageField(
        upload_to=img_path, verbose_name='Image', blank=True)
    sticky = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        self.sage = False
        super(Post, self).__init__(*args, **kwargs)

    def clean(self):
        if self.board.textboard:
            if not self.text:
                raise ValidationError('Submit text.')
            # XXX: in this case form shouldn't provide image input in first place
            if self.image:
                raise ValidationError('Board is text only.')
        else:
            if not (self.text or self.image):
                raise ValidationError('Submit text or/and upload image.')
        if self.thread:  # is reply
            thread = self.thread
            if thread.closed:
                raise ValidationError('Thread is closed.')
            if self.image and thread.post_set.filter(~models.Q(image='')).count() >= self.board.thread_img_limit:
                raise ValidationError('Image limit has been reached.')
        else:  # is thread
            if not self.image and self.board.op_requires_img:
                raise ValidationError('OP required to have an image.')

    def save(self, *args, **kwargs):
        # posts do not have a pk and timestamp until saved to db
        # thus instance.pk and self.timestamp return None
        # breaking img_path() and following bump set respectively
        if self.pk is None:
            img = self.image
            self.image = None
            super(Post, self).save(*args, **kwargs)
            self.image = img
            # on upload image will automatically be renamed
            # based on img_path() as originally intended

        if self.thread:  # is reply
            # XXX: maybe let bump be Null for replies
            self.bump = self.timestamp
            # required to first save an instance
            # changes directly on self.thread won't be saved
            thread = self.thread
            if not self.sage:
                # bump thread unless sage is True
                thread.bump = self.timestamp
            thread.save()
        elif not self.bump:
            # happens during thread creation
            # but not when thread.save() above is called
            self.bump = self.timestamp

        # happens only once since afterwards #password
        # is removed from the author field
        if '#' in self.author:
            usr, pwd = self.author.rsplit('#')
            hashpwd = hashlib.sha256(
                self.author.encode('utf-8')).hexdigest()[:10]
            self.author = usr
            self.tripcode = hashpwd

        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if not self.thread:
            return reverse('thread', kwargs={'board': self.board, 'thread': self.pk})
        else:
            return self.thread.get_absolute_url() + f'#p{self.pk}'
