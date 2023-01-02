from django.forms import ModelForm
from simplemathcaptcha.fields import MathCaptchaField

from .models import Post


class NewThreadForm(ModelForm):
    captcha = MathCaptchaField()

    class Meta:
        model = Post
        fields = [
            'author', 'subject', 'text', 'image'
        ]


class NewReplyForm(ModelForm):
    captcha = MathCaptchaField()

    class Meta:
        model = Post
        fields = [
            'author', 'text', 'image'
        ]
