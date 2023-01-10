import re

from django import template
from django.utils.safestring import mark_safe
from precise_bbcode.bbcode import get_parser

from ..models import Board, Post

try:
    bbcode_parser = get_parser()
except:
    exit

register = template.Library()

# from https://stackoverflow.com/a/11725011
urlregex = r'(^(https?:\/\/)?[0-9a-zA-Z]+\.[-_0-9a-zA-Z]+\.[0-9a-zA-Z]+$)'

BOARD = None


# usually in chan boards posts don't share id namespace across boards
# and post_link() shouldn't cross-board link
# currently in this chan they do
# and post_link() will change text showing board having post
# caution that this is only render-wise and dependenance on this functionality
# may break if id namespace is split per board

def post_link(match):
    post_id = match.group(1)
    if Post.objects.filter(pk=post_id).exists():
        post = Post.objects.get(pk=post_id)
        if BOARD == post.board.ln:
            return f"<a href=\"{post.get_absolute_url()}\">&gt;&gt;{post_id}</a>"
        else:
            return f"<a href=\"{post.get_absolute_url()}\">&gt;&gt;&gt;/{post.board.ln}/{post_id}</a>"

    return f"&gt;&gt;{post_id}"


def board_link(match):
    board_ln = match.group(1)
    if Board.objects.filter(ln=board_ln).exists():
        board = Board.objects.get(ln=board_ln)
        ret = f"<a href=\"{board.get_absolute_url()}\">&gt;&gt;&gt;/{board_ln}/</a>"
    else:
        ret = f"&gt;&gt;&gt;/{board_ln}/"

    return ret


def cross_board_post_link(match):
    board_ln, post_id = match.group(1, 2)
    if Post.objects.filter(pk=post_id).exists():
        post = Post.objects.get(pk=post_id)
        if board_ln == post.board.ln:
            return f"<a href=\"{post.get_absolute_url()}\">&gt;&gt;&gt;/{board_ln}/{post_id}</a>"

    return f"&gt;&gt;&gt;/{board_ln}/{post_id}"


@register.simple_tag
def post_render(board, post):
    global BOARD  # phew, global
    BOARD = board
    post = bbcode_parser.render(post)
    post = re.sub(r'&gt;&gt;(\d+)', post_link, post)
    post = re.sub(r'&gt;&gt;&gt;/([a-z]+)/(?!\d+)', board_link, post)
    post = re.sub(r'&gt;&gt;&gt;/([a-z]+)/(\d+)', cross_board_post_link, post)
    post = re.sub(urlregex, "<a href=\"\g<0>\">\g<0></a>", post)
    # XXX: looks terrible
    post = '<br />'.join(re.sub(r'^(&gt;.+)$', "<span class=\"quotetext\">\g<1></span>", line)
                         for line in post.split('<br />'))
    return mark_safe(post)
