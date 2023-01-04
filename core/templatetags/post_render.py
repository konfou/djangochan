import re

from django import template
from django.utils.safestring import mark_safe
from precise_bbcode.bbcode import get_parser

register = template.Library()

try:
    bbcode_parser = get_parser()
except:
    exit

# from https://stackoverflow.com/a/11725011
urlregex = r'(^(https?:\/\/)?[0-9a-zA-Z]+\.[-_0-9a-zA-Z]+\.[0-9a-zA-Z]+$)'

@register.simple_tag
def post_render(post):
    post = bbcode_parser.render(post)
    post = re.sub(r'&gt;&gt;(\d+)', "<a href=\"#\g<1>\">&gt;&gt;\g<1></a>", post)
    post = re.sub(r'&gt;&gt;&gt;/([a-z]+)/(\d+)', "<a href=\"/\g<1>/\g<2>\">&gt;&gt;&gt;/\g<1>/\g<2></a>", post)
    post = re.sub(r'&gt;&gt;&gt;/([a-z]+)/', "<a href=\"/\g<1>/\">&gt;&gt;&gt;/\g<1>/</a>", post)
    post = re.sub(urlregex, "<a href=\"\g<0>\">\g<0></a>", post)
    # XXX: looks terrible
    post = '<br />'.join(re.sub(r'^(&gt;.+)$', "<span class=\"quotetext\">\g<1></span>", line) for line in post.split('<br />'))
    return mark_safe(post)
