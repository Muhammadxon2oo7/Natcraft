# store/serializers.py
from rest_framework import serializers
from .models import Category, Product, CustomUser, ProductImage
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^\+998[0-9]{9}$', 
                message="Telefon raqam +998XXXXXXXXX formatida bo'lishi kerak"
            )
        ]
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name', 
            'email', 'phone_number', 'bio', 
            'profile_image'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    category = CategorySerializer(read_only=True)
    seller = UserSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['seller']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        category_data = validated_data.pop('category', None)
        seller_data = validated_data.pop('seller', None)

        # Productni yaratish
        product = Product.objects.create(
            category=category_data, 
            seller=seller_data, 
            **validated_data
        )
        
        # Rasmlarni qo'shish
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])
        category_data = validated_data.pop('category', None)
        seller_data = validated_data.pop('seller', None)

        instance = super().update(instance, validated_data)

        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                ProductImage.objects.create(product=instance, **image_data)
        
        return instance
