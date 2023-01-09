from django import forms
from django.conf import settings
from simplemathcaptcha.fields import MathCaptchaField
from simplemathcaptcha.widgets import MathCaptchaWidget

from .models import Post

# TODO: simplify this


class NewThreadForm(forms.ModelForm):
    if settings.CAPTCHA:
        captcha = MathCaptchaField(widget=MathCaptchaWidget(
            question_tmpl="%(num1)i %(operator)s %(num2)i = "))

    options = forms.CharField(
        label='Options', required=False, empty_value=None)

    class Meta:
        model = Post
        fields = [
            'author', 'subject', 'text', 'image'
        ]

    field_order = ['author', 'options']


class NewReplyForm(forms.ModelForm):
    if settings.CAPTCHA:
        captcha = MathCaptchaField(widget=MathCaptchaWidget(
            question_tmpl="%(num1)i %(operator)s %(num2)i = "))

    options = forms.CharField(
        label='Options', required=False, empty_value=None)

    class Meta:
        model = Post
        fields = [
            'author', 'text', 'image'
        ]

    field_order = ['author', 'options']
