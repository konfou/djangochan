from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.urls import reverse

import sys
from io import BytesIO
from PIL import Image


def rename_upload_img(instance, filename):
    ext = filename.split('.')[-1]
    return 'img/{}.{}'.format(instance.pk, ext)

def rename_upload_thumb(instance, filename):
    ext = filename.split('.')[-1]
    return 'img/{}_s.{}'.format(instance.pk, ext)

class Board(models.Model):
    name = models.CharField(max_length=16)
    ln = models.SlugField(max_length=8)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.ln

    def get_absolute_url(self):
        return reverse('board', kwargs={'board': self.ln})


class Post(models.Model):
    board = models.ForeignKey(
        'Board', on_delete=models.CASCADE, null=False, blank=False)
    thread = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)
    author = models.CharField(max_length=32, default='Anonymous')
    subject = models.CharField(max_length=64, null=True, blank=True)
    text = models.TextField()
    image = models.ImageField(
        upload_to=rename_upload_img, verbose_name='Image', blank=True)
    thumb = models.ImageField(
        upload_to=rename_upload_thumb, verbose_name='Thumbnail', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    bump = models.DateTimeField(auto_now=True)
    cookie = models.CharField(max_length=32, null=True, blank=True)

    def save(self, **kwargs):
        o_size = (300, 300)
        o_thumb = BytesIO()

        # img = Image.open(self.image)
        # img_name = self.image.name.split('.')[0]

        # if img.height > 300 or img.width > 300:
        #     img.thumbnail(o_size)
        #     img.save(o_thumb, format='JPEG', quality=90)

        # self.image_thumb = InMemoryUploadedFile(o_thumb, 'ImageField', 'thumb.jpg', 'image/jpeg', sys.getsizeof(o_thumb), None)
        super(Post, self).save()

    def get_absolute_url(self):
        return reverse('thread', kwargs={'board': self.board, 'thread': self.pk})
