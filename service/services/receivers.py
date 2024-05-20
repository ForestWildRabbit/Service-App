from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(post_delete)
def delete_cache_total_price(*args, **kwargs):
    cache_key_name = 'PRICE_CACHE_NAME'
    cache.delete(settings.CACHES_DATA[cache_key_name])
