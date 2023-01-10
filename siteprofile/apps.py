# By @pydatageek under CC BY-SA 4.0
# https://stackoverflow.com/a/64288644
from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate


def create_default_site_profile(sender, **kwargs):
    from django.contrib.sites.models import Site
    from core.models import SiteProfile

    if not SiteProfile.objects.exists():
        site = Site.objects.get(id=getattr(settings, 'SITE_ID', 1))
        SiteProfile.objects.create(site=site)


class SiteProfileConfig(AppConfig):
    name = 'siteprofile'
    verbose_name = 'SiteProfile'

    def ready(self):
        post_migrate.connect(create_default_site_profile, sender=self)
        from .signals import create_site_profile
