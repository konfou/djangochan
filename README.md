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
this repo ~~and resets once daily~~ (gonna be doing the reset
irregularly so it isn't permanently in wasteland mode).

## TODO

- refactor search, thread, incl/threads_list, reply templates (currently
  they share large parts)
- add per-board max filesize+
- add ip-based post limit (needed to prevent spam, theoretically server
  could do that)
- add ip-based ban (probably useless for users, and actual spam bots
  could be handled by server)
- improve htmx utilization (currently overlying on hx-boost)
- improve site and admin panel design (django project site has cool
  design and colorscheme to base on, also check simple.css)
- improve caching, maybe save rendered text
- provide posting via JSON API (requires changes to simple-math-captcha)
- add pagination
- add capcodes
- quote link preview utilizing the htmx or json api
- file deduplication+
- file filter+
- add tests to all apps+

Project considered feature complete after those are done.

## Dependencies

- Django
- django-environ
- django-precise-bbcode
- django-simple-math-captcha
- djangorestframework
- sorl-thumbnail

## Similar

Projects to ~~copy ideas~~ get inspiration from.

- [Blazechan](https://gitgud.io/blazechan/blazechan) (2016-2018; &REST)
- [Monki](https://github.com/exclude/monki) (2017)
- [Hexchan](https://github.com/binakot/hexchan-engine) (2018-2019)
- [Picoboard](https://github.com/anonim-legivon/picoboard) (2019; REST)
- [Maniwani](https://github.com/DangerOnTheRanger/maniwani) (2018-2021; Flask)
