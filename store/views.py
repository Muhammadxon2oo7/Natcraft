from django.shortcuts import render

# Create your views here.
# store/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import random

from .models import Category, Product, CustomUser
from .serializers import CategorySerializer, ProductSerializer, UserSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     # Kategoriya bo'yicha filtrlash
    #     category_name = self.request.query_params.get('category', None)
    #     if category_name:
    #         return Product.objects.filter(category__name=category_name)
    #     return super().get_queryset()


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
    
    def get_queryset(self):
        # Kategoriya bo'yicha filtrlash
        category_name = self.request.query_params.get('category', None)
        if category_name:
            return Product.objects.filter(category__name=category_name)
        return super().get_queryset()

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Tasdiqlash kodi yaratish
        verification_code = str(random.randint(100000, 999999))
        user = serializer.save(verification_code=verification_code, is_verified=False)
        
        # TODO: SMS xizmati orqali verification_code ni telefonga yuborish
        print(f"Verification code for {user.phone_number}: {verification_code}")
        
        return Response({
            'message': 'Ro\'yxatdan o\'tish muvaffaqiyatli. Tasdiqlash kodini tekshiring.',
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def verify_phone(self, request):
        user_id = request.data.get('user_id')
        verification_code = request.data.get('verification_code')
        
        try:
            user = CustomUser.objects.get(id=user_id, verification_code=verification_code)
            user.is_verified = True
            user.save()
            
            # Token yaratish
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'Telefon raqami tasdiqlandi',
                'token': token.key
            })
        except CustomUser.DoesNotExist:
            return Response({
                'error': 'Tasdiqlash kodi noto\'g\'ri'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id
            })
        else:
            return Response({
                'error': 'Login yoki parol noto\'g\'ri'
            }, status=status.HTTP_401_UNAUTHORIZED)