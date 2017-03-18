from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
import timedelta
import math
# Create your models here.

class Treatment(models.Model):
    name = models.CharField(max_length=30, unique=True)
    cost_price = models.IntegerField(blank=False, null=False)
    selling_price = models.IntegerField(blank = False, null = False)
    description = models.TextField(blank=False, null=False, default=' ')
    duration = timedelta.fields.TimedeltaField()
    store = models.ForeignKey('Store', on_delete=models.DO_NOTHING)
    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Customer(models.Model):
    class Meta:
        unique_together = (('name', 'contact'),)
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    contact = models.CharField(max_length=11)
    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("appointcreate", kwargs={"cid":self.id})

class Store(models.Model):
    class Meta:
        unique_together = (('name', 'address'),)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=11)
    address = models.CharField(max_length=100)
    def __unicode__(self):
        return self.address

    def __str__(self):
        return self.address

    def get_absolute_url(self):
        return reverse("store", kwargs={"id":self.id})

class Offer(models.Model):
    name = models.CharField(max_length = 100, null = False, blank = False)
    offer = models.FloatField(null = False, blank = False)
    treatment = models.ManyToManyField('Treatment', blank = True)
    end_date = models.DateTimeField(default = datetime.now, blank = True)
    store = models.ForeignKey('Store', on_delete=models.DO_NOTHING)
    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name
