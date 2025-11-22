from rest_framework import exceptions
from rest_framework.request import Request
from rest_framework.permissions import BasePermission
from rest_framework.authentication import BaseAuthentication
from loguru import logger


class APIException:
    auth_name = "HTTP_AUTHORIZATION"
    allow_path = ("/docs/",)

    def auth_token(self, request):
        return request.META.get(self.auth_name, "")

    def auth_401(self, detail="认证失败"):
        raise exceptions.AuthenticationFailed(detail=detail)

    def auth_403(self, detail="没有访问权限"):
        raise exceptions.PermissionDenied(detail=detail)

    def exceptions(self, detail=None, code=None):
        raise exceptions.APIException(detail=detail, code=code)


class UserAuthentication(BaseAuthentication, APIException):
    """
    authentication backend using `django-oauth-toolkit`
    """

    def authenticate(self, request: Request):
        """"""
        return None


class UserPermission(BasePermission, APIException):
    def has_permission(self, request: Request, view):
        """让所有用户都有权限"""
        return True

    def has_object_permission(self, request, view, obj):
        """用户是否有权限访问添加了权限控制类的数据对象"""
        return True
