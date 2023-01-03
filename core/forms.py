from django.forms import ModelForm
from simplemathcaptcha.fields import MathCaptchaField
from simplemathcaptcha.widgets import MathCaptchaWidget

from .models import Post


class NewThreadForm(ModelForm):
    captcha = MathCaptchaField(widget=MathCaptchaWidget(question_tmpl="%(num1)i %(operator)s %(num2)i = "))

    class Meta:
        model = Post
        fields = [
            'author', 'subject', 'text', 'image'
        ]


class NewReplyForm(ModelForm):
    captcha = MathCaptchaField(widget=MathCaptchaWidget(question_tmpl="%(num1)i %(operator)s %(num2)i = "))

    class Meta:
        model = Post
        fields = [
            'author', 'text', 'image'
        ]
