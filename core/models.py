from django.db import models
from django.urls import reverse


class Board(models.Model):
    name = models.CharField(max_length=16)
    ln = models.SlugField(max_length=8)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.ln

    def get_absolute_url(self):
        return reverse('board', kwargs={'board': self.ln})

class Post(models.Model):
    board = models.ForeignKey('Board', on_delete=models.CASCADE, null=False, blank=False)
    thread = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    author = models.CharField(max_length=32, default='Anonymous')
    #subject = models.CharField(max_length=64, null=True, blank=True)
    text = models.TextField()
    image = models.ImageField(upload_to='img/', verbose_name='Image', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    bump = models.DateTimeField(auto_now=True)
    cookie = models.CharField(max_length=32, null=True)

    def get_absolute_url(self):
        return reverse('thread', kwargs={'board': self.object.board.ln, 'thread': self.object.pk})
