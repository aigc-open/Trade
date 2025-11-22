import os
from pathlib import Path
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings


_tag = "文档"


class DocsViewSet(viewsets.ViewSet):
    """文档API视图集"""
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        method='get',
        operation_summary="获取AI交易系统使用文档",
        tags=[_tag],
        responses={
            200: openapi.Response(
                description="文档内容（Markdown格式）",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'content': openapi.Schema(type=openapi.TYPE_STRING, description='文档内容'),
                        'filename': openapi.Schema(type=openapi.TYPE_STRING, description='文件名'),
                        'last_modified': openapi.Schema(type=openapi.TYPE_STRING, description='最后修改时间'),
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='system-guide')
    def system_guide(self, request):
        """获取AI交易系统使用指南"""
        try:
            # 文档在 server 目录下
            doc_path = Path(settings.BASE_DIR) / 'AI_TRADER_README.md'
            
            if not doc_path.exists():
                return Response(
                    {'error': '文档文件不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 读取文档内容
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 获取文件修改时间
            import datetime
            mtime = os.path.getmtime(doc_path)
            last_modified = datetime.datetime.fromtimestamp(mtime).isoformat()
            
            return Response({
                'content': content,
                'filename': 'AI_TRADER_README.md',
                'last_modified': last_modified
            })
            
        except Exception as e:
            return Response(
                {'error': f'读取文档失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        method='get',
        operation_summary="获取文档列表",
        tags=[_tag],
        responses={
            200: openapi.Response(
                description="可用文档列表",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description='文档名称'),
                            'key': openapi.Schema(type=openapi.TYPE_STRING, description='文档标识'),
                            'description': openapi.Schema(type=openapi.TYPE_STRING, description='文档描述'),
                        }
                    )
                )
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='list')
    def list_docs(self, request):
        """获取可用文档列表"""
        docs = [
            {
                'name': 'AI交易系统使用指南',
                'key': 'system-guide',
                'description': 'AI自主交易智能体系统完整使用文档，包含系统架构、功能说明、API接口、快速开始等'
            }
        ]
        return Response(docs)

