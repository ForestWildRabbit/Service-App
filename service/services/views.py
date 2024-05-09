from rest_framework.viewsets import ReadOnlyModelViewSet

from services.models import Subscription
from services.serializers import SubscriptionSerializer


class SubscriptionAPIView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
