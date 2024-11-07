from django.contrib import admin

# Register your models here.

from django.contrib.auth.admin import UserAdmin
from .models import Category, Product, CustomUser, ProductImage

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'phone_number', 'is_verified']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'bio', 'profile_image', 'is_verified', 'one_id_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number',)}),
    )

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Bu yangi satrlarni avtomatik ravishda ko'rsatishni oldini oladi

    can_delete = True
    max_num = 10  # Maximum 10 ta rasm
    min_num = 1   # Minimal rasm soni
    verbose_name = "Product Image"
    verbose_name_plural = "Product Images"

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'seller', 'price', 'stock', 'created_at']
    list_filter = ['name', 'category', 'seller']
    search_fields = ['name', 'description',]
    inlines = [ProductImageInline]



class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

# Modellarni admin panelga ro'yxatdan o'tkazish
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductImage)