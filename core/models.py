import crypt
import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Case, When
from django.urls import reverse
from django.utils import timezone
from siteprofile.models import SiteProfileBase

TRANS_TABLE = str.maketrans(":;<=>?@[\]^_`", "ABCDEFGabcdef")


def img_path(instance, filename):
    ext = filename.rsplit('.')[-1]
    return f"{instance.board}/{instance.pk}.{ext}"


# for siteprofile app
class SiteProfile(SiteProfileBase):
    # site-wide settings
    title = models.CharField(max_length=64, default=getattr(
        settings, 'SITE_TITLE', 'djangochan'))
    description = models.CharField(max_length=128, default=getattr(
        settings, 'SITE_DESCRIPTION', 'django-powered imageboard'))
    issue = models.TextField(default=getattr(
        settings, 'SITE_ISSUE', 'A message shown on index.'))


class Board(models.Model):
    # info
    name = models.CharField(max_length=16)
    ln = models.SlugField(max_length=8)
    description = models.TextField(blank=True)
    # settings
    max_threads = models.IntegerField(null=True, default=100)
    thread_bump_limit = models.IntegerField(null=True, default=500)
    thread_img_limit = models.IntegerField(null=True, default=150)
    archive_retention_time = models.TimeField(null=True, blank=True)
    # bool settings
    op_requires_img = models.BooleanField(default=False)
    textboard = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return self.ln

    def get_absolute_url(self):
        return reverse('board', kwargs={'board': self.ln})

    def get_threads_count(self):
        return self.post_set.filter(thread__isnull=True).count()

    def is_max(self):
        return self.get_threads_count() >= self.max_threads


class Post(models.Model):
    # server generated
    board = models.ForeignKey(
        'Board', on_delete=models.CASCADE, null=False, blank=False)
    thread = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    cookie = models.CharField(max_length=32, blank=True)
    # thread
    bump = models.DateTimeField(null=True)
    closed = models.BooleanField(default=False)
    sticky = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    # user provided
    author = models.CharField(max_length=32, default='Anonymous')
    tripcode = models.CharField(max_length=10, blank=True)
    secure = models.BooleanField(default=False)
    subject = models.CharField(max_length=64, blank=True)
    text = models.TextField(blank=True)
    text_rendered = models.TextField(blank=True)
    # NOTE: updating img won't overwrite old one but save new
    # not issue because image isn't meant to be modified
    image = models.ImageField(
        upload_to=img_path, verbose_name='Image', blank=True)
    filename = models.CharField(max_length=64, blank=True)

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
            if self.board.closed:
                raise ValidationError('Board is closed.')
            if not self.image and self.board.op_requires_img:
                raise ValidationError('OP required to have an image.')

    def delete(self, *args, **kwargs):
        storage = self.image.storage
        if self.image and storage.exists(self.image.name):
            storage.delete(self.image.name)
        super().delete()

    def save(self, *args, **kwargs):
        # posts do not have a pk and timestamp until saved to db
        # thus instance.pk and self.timestamp return None
        # breaking img_path() and following bump set respectively
        if self.pk is None:
            img = self.image
            self.image = None
            super(Post, self).save(*args, **kwargs)
            self.image = img
            self.filename = img.name
            # on upload image will automatically be renamed
            # based on img_path() as originally intended

        if self.thread:  # is reply
            # XXX: maybe let bump be Null for replies
            self.bump = self.timestamp
            # bump thread unless saged by option or auto
            if not self.sage and not self.thread.post_set.count() >= self.board.thread_bump_limit:
                # required to first save an instance
                # changes directly on self.thread won't be saved
                thread = self.thread
                thread.bump = self.timestamp
                thread.save()
        elif not self.bump:
            # happens during thread creation
            # but not when thread.save() above is called
            self.bump = self.timestamp
            if not self.archived and self.board.is_max():
                # XXX: [0]/latest() will return the new thread since it has None bump
                bottom = self.board.post_set.filter(
                    thread__isnull=True, sticky=False, archived=False).order_by('bump')[1]
                bottom.archived = True
                bottom.closed = True
                bottom.save()

        if not self.tripcode and '#' in self.author:
            usr, pwd = self.author.rsplit('#', 1)
            # algo: https://github.com/ctrlcctrlv/tripkeys/blob/master/doc/2ch_tripcode_annotated.pl
            salt = (pwd + 'H..')[1:3]
            salt = re.sub('[^\.-z]', '.', salt)
            salt = salt.translate(TRANS_TABLE)
            if usr[-1] == '#':
                salt = '$1$' + self.author + '$'
                usr = usr[:-1]
                self.secure = True
            self.author = usr
            self.tripcode = crypt.crypt(pwd, salt)[-10:]

        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if not self.thread:
            return reverse('thread', kwargs={'board': self.board, 'thread': self.pk})
        else:
            return self.thread.get_absolute_url() + f'#p{self.pk}'

    def get_delete_url(self):
        return reverse('post-delete', kwargs={'board': self.board, 'post': self.pk})

    def get_report_url(self):
        return reverse('post-report', kwargs={'board': self.board, 'post': self.pk})


class Report(models.Model):
    board = models.ForeignKey(
        'Board', on_delete=models.CASCADE, null=False, blank=False)
    post = models.ForeignKey(
        'Post', on_delete=models.CASCADE, null=False, blank=False)
    reason = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
