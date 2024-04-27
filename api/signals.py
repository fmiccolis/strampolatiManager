import logging

import jwt
import requests
from django.conf import settings

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from api.models import Event
from api.serializers import EventSerializer

logger = logging.getLogger('custom')


@receiver(post_save, sender=Event)
async def create_calendar_event(sender, instance: Event, created, **kwargs):
    if created:
        now = timezone.now()
        if instance.start_date < now:
            return
        serialized = EventSerializer(instance).data
        payload = {
            "data": serialized,
            "source": "development" if settings.DEBUG else "production"
        }
        with open('./static/keys/private.pem', 'r') as file:
            private = file.read()
        token = jwt.encode(payload, private, algorithm="RS256")
        gas_response = requests.post('https://script.google.com/macros/s/AKfycbzJKsrJNsS8hiOHNn2tWNFC0obvdrAAL5oG8XVOSMhLnTRtgijgIAE0-wwiDNakLw46/exec', data=token)


