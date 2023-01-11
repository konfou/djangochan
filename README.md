# djangochan

Learning Django building an imageboard.

*WARNING: Not production ready. Database schema not finalized.*

## TODO

- autogenerate pass for author to delete post/image
- add pagination
- add capcodes
- add ip-based post limit (needed to prevent spam)
- cache posts renderings
- per-board active thread limit, archive oldest bumped ones
- search engine

## Dependencies

- Django
- django-environ
- django-precise-bbcode
- django-simple-captcha
- djangorestframework
- sorl-thumbnail

## Similar

Projects to ~~copy ideas~~ get inspiration from.

- [Monki](https://github.com/exclude/monki) (2017)
- [Hexchan](https://github.com/binakot/hexchan-engine) (2018-2019)
- [Picoboard](https://github.com/anonim-legivon/picoboard) (2019; REST)
- [nawrocki/django-imageboard](https://github.com/michal-nawrocki/django_imageboard) (2020)
- [Maniwani](https://github.com/DangerOnTheRanger/maniwani) (2018-2021; Flask)
