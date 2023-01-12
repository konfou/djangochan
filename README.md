# djangochan

A django-powered image/textboard engine. It's split to a core app with
the boards and posts models, a boards app with hmtx-dynamic
template-based server-rendered front-end, and a read-only (for time
being) JSON API utilizing Django REST framework.

Before running via `manage.py` copy `.env.dist` to `.env` and
modify. Site profile (title, description, others) can be modified from
admin panel.

This is mainly an educational project for myself to learn Django, and as
a template to follow for future projects. Issues and bug reports
welcome, contributions too considering previous.

There's a test instance deployed on PythonAnywhere, linked in repo
details, where someone can check how project looks like. It updates from
this repo and resets once daily.

*WARNING: Not production ready. Database schema not finalized.*

## TODO

- improve htmx utilization (currently overlying on hx-boost)
- improve site and admin panel design (django project site has cool
  design and colorscheme to base on, also check simple.css)
- provide posting via JSON API (requires changes to simple-math-captcha)
- autogenerate pass for author to delete post/image
- add pagination
- add capcodes
- add ip-based post limit (needed to prevent spam, theoretically server
  could do that)
- add ip-based ban (probably useless for users, and actual spam bots
  could be handled by server)
- add report post
- add catalog view
- retain and make accessible original filename
- per-board active thread limit, archive oldest bumped ones
- quote link preview utilizing the htmx or json api
- search engine

Project considered feature complete after those are done.

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
