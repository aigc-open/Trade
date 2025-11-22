
import threading
import os
from loguru import logger
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions, status
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from utils.djSwagger import swagger_view
from apps import CustomPagination
from .models import TokenModel
from .serializers import TokenSerializer, TokenRateLimitSerializer
from django.shortcuts import get_object_or_404
from apps.middleware import CustomUserPermission, CustomUserAuthentication

# Create your views here.


_tag = "Token"


@method_decorator(name="create",
                  decorator=swagger_view.swagger_auto_schema(operation_summary=f"创建{_tag}", tags=[_tag]))
@method_decorator(name="list",
                  decorator=swagger_view.swagger_auto_schema(operation_summary=f"查询{_tag}", tags=[_tag]))
@method_decorator(name="destroy",
                  decorator=swagger_view.swagger_auto_schema(operation_summary=f"删除{_tag}", tags=[_tag]))
@method_decorator(name="retrieve",
                  decorator=swagger_view.swagger_auto_schema(operation_summary=f"查询{_tag}详情", tags=[_tag]))
@method_decorator(name="partial_update",
                  decorator=swagger_view.swagger_auto_schema(operation_summary=f"更新/编辑一个{_tag}", tags=[_tag]))
@method_decorator(name="update",
                  decorator=swagger_view.swagger_auto_schema(operation_summary=f"更新/编辑一个{_tag}", tags=[_tag]))
@method_decorator(name="set_token_limit",
                  decorator=swagger_view.swagger_auto_schema(operation_summary=f"更新/编辑一个{_tag}的速率", tags=[_tag]))
class TokenViewSet(viewsets.ModelViewSet):
    model_class = TokenModel
    queryset = model_class.objects.all().filter()
    serializer_class = TokenSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPagination
    permission_classes = [CustomUserPermission]
    authentication_classes = [CustomUserAuthentication]
    filter_class = []
    order_fields = []

    def get_queryset(self):
        # 🔧 处理Swagger文档生成时的匿名用户问题
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        
        if not self.request.user.is_authenticated:
            return self.queryset.none()
            
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["put"])
    def set_token_limit(self, request, pk=None):
        key = request.data["key"]
        token = get_object_or_404(TokenModel, pk=key)
        serializer = TokenRateLimitSerializer(token, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


