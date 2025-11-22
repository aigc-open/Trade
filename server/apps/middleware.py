import logging
import re
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin
from utils.djSwagger.permission_auth import UserAuthentication
from utils.djSwagger.permission_auth import UserPermission
from rest_framework.request import Request
from loguru import logger
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication as DRFTokenAuthentication
from apps.token.models import TokenModel
from rest_framework.authtoken.models import Token

User = get_user_model()


class CustomUserAuthentication(DRFTokenAuthentication):
    """
    自定义Token认证，通过token获取user对象
    """
    
    def authenticate(self, request):
        """
        通过Authorization header中的token获取用户
        """
        auth = self.get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        """
        根据token key获取用户
        """
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (token.user, token)

    def get_model(self):
        """
        返回token模型，优先使用DRF的Token模型
        """
        return Token

    def get_authorization_header(self, request):
        """
        从request中获取Authorization header
        """
        auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if isinstance(auth, str):
            auth = auth.encode('iso-8859-1')
        return auth


class CustomUserPermission(UserPermission):
    def has_permission(self, request: Request, view):
        """检查用户权限"""
        # 如果路径在允许列表中，直接返回True
        if hasattr(self, 'allow_path') and request.path in self.allow_path:
            return True
        
        # 打印当前用户信息用于调试
        logger.debug(f"Request user: {request.user}")
        logger.debug(f"Is authenticated: {request.user.is_authenticated}")
        
        # 如果用户已认证，返回True
        if request.user.is_authenticated:
            return True
        
        return False

    def has_object_permission(self, request, view, obj):
        """用户是否有权限访问添加了权限控制类的数据对象"""
        return True


class TokenAuthentication(DRFTokenAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """
    def get_model(self):
        return TokenModel


class AuthTokenMiddleware(DRFTokenAuthentication):
    """
    Middleware for OAuth2 user authentication

    This middleware is able to work along with AuthenticationMiddleware and its behaviour depends
    on the order it's processed with.

    If it comes *after* AuthenticationMiddleware and request.user is valid, leave it as is and does
    not proceed with token validation. If request.user is the Anonymous user proceeds and try to
    authenticate the user using the OAuth2 access token.

    If it comes *before* AuthenticationMiddleware, or AuthenticationMiddleware is not used at all,
    tries to authenticate user with the OAuth2 access token and set request.user field. Setting
    also request._cached_user field makes AuthenticationMiddleware use that instead of the one from
    the session.

    It also adds "Authorization" to the "Vary" header, so that django's cache middleware or a
    reverse proxy can create proper cache keys.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user, token = self.authenticate(request)

        if user and user.is_active:
            request.user = request._cached_user = user

        response = self.get_response(request)
        patch_vary_headers(response, ("Authorization",))
        return response
