# from random import randint

from precise_bbcode.bbcode.tag import BBCodeTag
from precise_bbcode.tag_pool import tag_pool


class SpoilerTag(BBCodeTag):
    name = 'spoiler'
    definition_string = '[spoiler]{TEXT}[/spoiler]'
    format_string = '<span class="spoiler">{TEXT}</span>'


# class RollTag(BBCodeTag):
#     name = 'roll'
#     definition_string = '[roll]'
#     format_string = '<span class="roll">Roll: ' + \
#         str(randint(1, 100)) + '</span>'

#     class Options:
#         standalone = True


tag_pool.register_tag(SpoilerTag)
# tag_pool.register_tag(RollTag)
