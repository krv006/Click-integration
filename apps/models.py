from django.db.models import Model
from django.db.models.fields import CharField, BooleanField, IntegerField


class Order(Model):
    costumer_name = CharField(max_length=255)
    address = CharField(max_length=255)
    total_cost = IntegerField()
    payment_method = CharField(max_length=255)
    is_paid = BooleanField(default=False)

    def __str__(self):
        return self.costumer_name
