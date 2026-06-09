from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone

def is_user_online(user):
    last_seen = cache.get(f'seen_{user.id}')
    if last_seen:
        return timezone.now() - last_seen < timedelta(seconds=120)
    return False
