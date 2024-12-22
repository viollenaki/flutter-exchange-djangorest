from django.db import models

# Create your models here.
class Event(models.Model):
    type = models.CharField(max_length=255)
    currency = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.type} - {self.currency} ({self.date})"
    
    class Meta:
        db_table = 'events'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-date']

class Currency(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'currencies'
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'
        ordering = ['name']

class User(models.Model):
    name = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['name']