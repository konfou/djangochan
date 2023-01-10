# By @pydatageek under CC BY-SA 4.0
# https://stackoverflow.com/a/64288644
from django.conf import settings
from django.contrib.sites.models import Site


def site_processor(request):
    try:
        return {
            'site': Site.objects.get_current()
        }
    except:
        Site.objects.create(
            id=getattr(settings, 'SITE_ID', 1),
            domain='example.com', name='example.com')
