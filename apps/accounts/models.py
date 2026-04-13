from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        return super().create_superuser(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
        ('supplier', 'Supplier'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='other'
    )

    objects = CustomUserManager()
    
    # Profile Fields
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role}, {self.gender})"

class RegularUser(CustomUser):
    class Meta:
        proxy = True
        verbose_name = "Regular User"
        verbose_name_plural = "Regular Users"

class Supplier(CustomUser):
    class Meta:
        proxy = True
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
