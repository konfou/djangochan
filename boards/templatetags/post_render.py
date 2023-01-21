import re
import random

from django import template
from django.utils.safestring import mark_safe
from precise_bbcode.bbcode import get_parser

from core.models import Board, Post

try:
    bbcode_parser = get_parser()
except:
    exit

register = template.Library()

# from https://stackoverflow.com/a/11725011
urlregex = r'(^(https?:\/\/)?[0-9a-zA-Z]+\.[-_0-9a-zA-Z]+\.[0-9a-zA-Z]+$)'

THREAD = None


# usually in chan boards posts don't share id namespace across boards
# and post_link() shouldn't cross-board link
# currently in this chan they do
# and post_link() will change text showing board having post
# caution that this is only render-wise and dependenance on this functionality
# may break if id namespace is split per board

def post_link(match):
    target_id = match.group(1)
    if Post.objects.filter(pk=target_id).exists():
        target = Post.objects.get(pk=target_id)
        if int(target_id) == THREAD.pk:
            return f"<a href=\"{target.get_absolute_url()}#top\" hx-boost=\"true\">&gt;&gt;{target_id} (OP)</a>"
        elif THREAD.post_set.filter(pk=target_id).exists():
            return f"<a href=\"{target.get_absolute_url()}\" hx-boost=\"true\">&gt;&gt;{target_id}</a>"
        elif target.board.ln == THREAD.board.ln:
            return f"<a href=\"{target.get_absolute_url()}\" hx-boost=\"true\">&gt;&gt;{target_id} (cross-thread)</a>"
        else:
            return f"<a href=\"{target.get_absolute_url()}\" hx-boost=\"true\">&gt;&gt;&gt;/{target.board.ln}/{target_id}</a>"

    return f"&gt;&gt;{target_id}"


def board_link(match):
    target_board_ln = match.group(1)
    if Board.objects.filter(ln=target_board_ln).exists():
        target_board = Board.objects.get(ln=target_board_ln)
        return f"<a href=\"{target_board.get_absolute_url()}\" hx-boost=\"true\">&gt;&gt;&gt;/{target_board_ln}/</a>"
    else:
        return f"&gt;&gt;&gt;/{target_board_ln}/"


def cross_board_post_link(match):
    target_board_ln, target_post_id = match.group(1, 2)
    if Post.objects.filter(pk=target_post_id).exists():
        target_post = Post.objects.get(pk=target_post_id)
        if target_board_ln == target_post.board.ln:
            return f"<a href=\"{target_post.get_absolute_url()}\" hx-boost=\"true\">&gt;&gt;&gt;/{target_board_ln}/{target_post_id}</a>"

    return f"&gt;&gt;&gt;/{target_board_ln}/{target_post_id}"

def roll(match):
    return '<span class="roll">Roll: ' + str(random.randint(1, 100)) + '</span>'


@register.simple_tag
def post_render(post):
    global THREAD  # phew, global
    THREAD = post.thread
    text = bbcode_parser.render(post.text)
    random.seed(post.timestamp)
    text = re.sub(r'\[roll]', roll, text)
    text = re.sub(r'&gt;&gt;(\d+)', post_link, text)
    text = re.sub(r'&gt;&gt;&gt;/([a-z]+)/(?!\d+)', board_link, text)
    text = re.sub(r'&gt;&gt;&gt;/([a-z]+)/(\d+)', cross_board_post_link, text)
    text = re.sub(urlregex, "<a href=\"\g<0>\">\g<0></a>", text)
    # XXX: looks terrible
    text = '<br />'.join(re.sub(r'^(&gt;.+)$', "<span class=\"quotetext\">\g<1></span>", line)
                         for line in text.split('<br />'))
    return mark_safe(text)
