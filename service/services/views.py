import random

from django.conf import settings
from django.db.models import Prefetch, QuerySet, Sum
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.core.cache import cache
from clients.models import Client
from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionAPIView(ReadOnlyModelViewSet):
    queryset = (Subscription.objects.all().prefetch_related(
        'plan',
        Prefetch('client', queryset=Client.objects.all().select_related('user').only('company_name', 'user__email'))
        )
    )
    serializer_class = SubscriptionSerializer

    def list(self, request, *args, **kwargs):
        queryset: QuerySet = self.filter_queryset(self.get_queryset())
        response = super().list(request, *args, **kwargs)

        cache_key_name = 'PRICE_CACHE_NAME'
        price_cache = cache.get(settings.CACHES_DATA[cache_key_name])
        jitter = random.randint(0, 10)

        if price_cache:
            total_price = price_cache
            cache.touch(settings.CACHES_DATA[cache_key_name], settings.CACHES_TTL['fast'] + jitter)
            settings.DJANGO_LOGGER.info(
                f"Cache {settings.CACHES_DATA[cache_key_name]} was extended"
                f" by {settings.CACHES_TTL['fast'] + jitter} sec.")
        else:
            total_price = queryset.aggregate(total=Sum('price')).get('total')
            cache.set(settings.CACHES_DATA[cache_key_name], total_price, settings.CACHES_TTL['fast'] + jitter)
            settings.DJANGO_LOGGER.info(
                f"Cache {settings.CACHES_DATA[cache_key_name]} was set"
                f" by {total_price}.")

        response_data = {
            'total_amount': total_price,
            'result': response.data,
        }
        response.data = response_data

        return response
