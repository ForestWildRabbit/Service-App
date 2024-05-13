from django.core.validators import MaxValueValidator
from django.db import models

from clients.models import Client
from services.tasks import set_price


class Service(models.Model):
    name = models.CharField(max_length=50)
    full_price = models.PositiveIntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__full_price = self.full_price

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.full_price != self.__full_price:  # on change full_price field
            for subscription in self.subscriptions.all():   # related name
                set_price.delay(subscription.id)

        return super().save(force_insert, force_update, using, update_fields)


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount'),
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=10)
    discount_percent = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.discount_percent != self.__discount_percent:  # on change discount_percent field
            for subscription in self.subscriptions.all():   # related name
                set_price.delay(subscription.id)

        return super().save(force_insert, force_update, using, update_fields)


class Subscription(models.Model):
    client = models.ForeignKey(Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.PositiveIntegerField(default=0)


