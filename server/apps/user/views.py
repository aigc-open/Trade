import threading
import os
from loguru import logger
from django.shortcuts import render
from rest_framework import viewsets, status, authentication
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from .models import UserModel
from .serializers import (
    UserSerializer, LoginSerializer, UserProfileSerializer
)
from apps.token.models import TokenModel


# Create your views here.


_tag = "User"


class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图集"""
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    
    def get_permissions(self):
        """根据不同的action设置不同的权限"""
        if self.action in ['create', 'login']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """根据不同的action选择不同的序列化器"""
        if self.action == 'login':
            return LoginSerializer
        elif self.action in ['profile', 'update_profile']:
            return UserProfileSerializer
        return UserSerializer
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """用户登录"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        login(request, user)
        
        # 获取或创建DRF token
        drf_token, created = Token.objects.get_or_create(user=user)
        
        # 获取或创建自定义TokenModel
        custom_token, created = TokenModel.objects.get_or_create(
            user=user,
            defaults={'key': drf_token.key}
        )
        
        # 如果自定义token已存在但key不同，更新key
        if not created and custom_token.key != drf_token.key:
            custom_token.key = drf_token.key
            custom_token.save()
        
        return Response({
            'token': drf_token.key,
            'user': UserProfileSerializer(user).data,
            'message': '登录成功'
        })
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """用户登出"""
        logout(request)
        return Response({'message': '登出成功'})
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """更新当前用户信息"""
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码"""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {'error': '请提供旧密码和新密码'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证旧密码
        if not user.check_password(old_password):
            return Response(
                {'error': '旧密码不正确'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 设置新密码
        user.set_password(new_password)
        user.save()
        
        return Response({'message': '密码修改成功'})

