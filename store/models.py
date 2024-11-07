from django.db import models

# Create your models here.
# store/models.py
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='profile_images/', 
        blank=True, 
        null=True
    )
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(
        max_length=6, 
        blank=True, 
        null=True
    )
    one_id_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


def validate_3d_file(value):
    valid_extensions = ['obj', 'stl', 'fbx', 'gltf']
    return FileExtensionValidator(valid_extensions)(value)

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        related_name='products', 
        null=True
    )
    seller = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='products'
    )
    stock = models.PositiveIntegerField(default=0)
    model_3d = models.FileField(
        upload_to='3d_models/', 
        validators=[validate_3d_file],
        blank=True,
        null=True
    )
    address = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
            if self.pk:  # Bu yerda Product obyekti saqlangan bo'lsa tekshiriladi
                if self.images.count() >= 10:
                    raise ValidationError("Maximum 10 ta rasm yuklab olinishi mumkin.")

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"