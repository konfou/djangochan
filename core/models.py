import hashlib

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
    bump = models.DateTimeField()
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

    def save(self, *args, **kwargs):
        # if post is reply won't modify post.thread
        # in contrast to having auto_now option in DateTimeField
        self.bump = timezone.now()

        if '#' in self.author:
            usr, pwd = self.author.rsplit('#')
            hashpwd = hashlib.sha256(self.author.encode('utf-8')).hexdigest()[:10]
            self.author = usr
            self.tripcode = hashpwd

        # posts do not have a pk until saved to db
        # thus instance.pk returns None breaking img_path()
        if self.pk is None:
            img = self.image
            self.image = None
            super(Post, self).save(*args, **kwargs)
            self.image = img
            # on upload image will automatically be renamed
            # based on img_path() as originally intended

        # if post is reply will modify post.thread
        if self.thread:
            # required to first save an instance
            # changes directly on self.thread won't be saved
            thread = self.thread
            if kwargs.get('sage', False):
                # bump thread unless sage=True is passed
                # for consistency use this/latest post.timestamp
                # rather calling timezone.now() again
                thread.bump = self.timestamp

            thread.save()

        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if not self.thread:
            return reverse('thread', kwargs={'board': self.board, 'thread': self.pk})
        else:
            return self.thread.get_absolute_url() + f'#p{self.pk}'
