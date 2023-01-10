from django import forms
from django.conf import settings
from simplemathcaptcha.fields import MathCaptchaField
from simplemathcaptcha.widgets import MathCaptchaWidget

from .models import Post


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


class NewReplyForm(NewThreadForm):
    class Meta(NewThreadForm.Meta):
        exclude = [
            'subject'
        ]

    def save(self, *args, **kwargs):
        opts = kwargs.pop('opts', None)
        if opts is not None:
            if 'sage' in opts:
                self.instance.sage = True

        super(NewReplyForm, self).save(*args, **kwargs)
