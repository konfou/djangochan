# By @pydatageek under CC BY-SA 4.0
# https://stackoverflow.com/a/64288644
from django.contrib.sites.models import Site
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver

from core.models import SiteProfile


@receiver(post_save, sender=Site)
def create_site_profile(sender, instance, **kwargs):
    profile, created = SiteProfile.objects.update_or_create(site=instance)
    if not created:
        profile.save()
