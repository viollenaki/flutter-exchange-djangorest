from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.
class Event(models.Model):
    type = models.CharField(max_length=255)
    currency = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.CharField(max_length=5)  
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

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



class User(models.Model):  # Changed from AbstractBaseUser to models.Model
    username = models.CharField(max_length=255)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=255, unique=True)  
    isSuperUser = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'users'
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        
    def save(self, *args, **kwargs):
        if not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
            # Если пароль еще не захеширован, хешируем его
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.email