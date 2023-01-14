# Selecting the current time zone
# https://docs.djangoproject.com/en/4.1/topics/i18n/timezones/

import zoneinfo
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            tzname = request.COOKIES.get("tzname")
            if tzname:
                timezone.activate(zoneinfo.ZoneInfo(tzname))
            else:
                timezone.deactivate()
        except:
            timezone.deactivate()

        return self.get_response(request)
