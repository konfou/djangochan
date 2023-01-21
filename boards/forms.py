from django import forms
from django.conf import settings
from simplemathcaptcha.fields import MathCaptchaField
from simplemathcaptcha.widgets import MathCaptchaWidget

from core.models import Post, Report


class NewThreadForm(forms.ModelForm):
    template_name = "boards/new_post_form.html"

    if settings.CAPTCHA:
        captcha = MathCaptchaField(widget=MathCaptchaWidget(
            question_tmpl="%(num1)i %(operator)s %(num2)i = "))

    options = forms.CharField(
        label='Options', required=False, empty_value='')

    class Meta:
        model = Post
        fields = [
            'author', 'subject', 'text', 'image'
        ]

    field_order = ['author', 'options']


class NewReplyForm(NewThreadForm):
    template_name = "boards/new_post_form.html"

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


class ReportPostForm(forms.ModelForm):
    if settings.CAPTCHA:
        captcha = MathCaptchaField(widget=MathCaptchaWidget(
            question_tmpl="%(num1)i %(operator)s %(num2)i = "))

    class Meta:
        model = Report
        fields = [
            'reason'
        ]
