from django.forms import ModelForm

from .models import Post


class NewThreadForm(ModelForm):
    class Meta:
        model = Post
        fields = [
            'author', 'text'
        ]

class NewReplyForm(ModelForm):
    class Meta:
        model = Post
        fields = [
            'author', 'text'
        ]
