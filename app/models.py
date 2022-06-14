from django.db import models
from djongo.models.fields import ObjectIdField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from random import uniform

class Wallet(models.Model):
    _id = ObjectIdField()
    belongs_to = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    btc_balance = models.FloatField(default=uniform(1,10))
    usd_balance = models.FloatField(default=100000)

    class Meta:
        verbose_name = "Wallet"
        verbose_name_plural = "Wallet"
        ordering = ['belongs_to']
    
    def __str__(self):
        return str(self.belongs_to)

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(belongs_to=instance)
        instance.wallet.save()
  
class Order(models.Model):
    _id = ObjectIdField()
    profile = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    price = models.FloatField()
    quantity = models.FloatField()
    status = models.CharField(max_length=10, choices=(("pending", "pending"), ("completed", "completed")), default='pending')
    type = models.CharField(max_length=4, choices=(("buy", "buy"), ("sell", "sell")), default='')

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Order'
        ordering = ['-datetime']

    def __str__(self):
        return self.datetime.strftime("%d/%m/%Y, %H:%M:%S")
