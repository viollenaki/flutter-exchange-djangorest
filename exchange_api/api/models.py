from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission

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


class UserManager(models.Manager):
    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

    def create_user(self, username, email, password=None, phone=None, **extra_fields):
        user = self.model(username=username, email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, phone=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, phone, **extra_fields)

class User(models.Model): 
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=255, unique=True)  
    is_superuser = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='user_set',
        related_query_name='user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='user_set',
        related_query_name='user'
    )
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone']
    
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

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_staff(self):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True
    
    def has_perm(self, perm, obj=None):
        return True
    
    def get_username(self):
        return self.username

    def check_password(self, raw_password):
        return make_password(raw_password) == self.password

    objects = UserManager()
