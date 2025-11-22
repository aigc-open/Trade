# 基于django drf_yasg 封装
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view
from django.urls import path, re_path
from drf_yasg import openapi
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
import logging

logger = logging.getLogger(__name__)


class SwaggerConfig:
    def __init__(
        self,
        url=None,
        patterns=None,
        urlconf=None,
        public=False,
        validators=None,
        generator_class=None,
        authentication_classes=None,
        permission_classes=None,
    ):
        self.url = url
        self.patterns = patterns
        self.urlconf = urlconf
        self.public = public
        self.validators = validators
        self.generator_class = generator_class
        self.authentication_classes = authentication_classes
        self.permission_classes = permission_classes

    def paths(
        self,
        title,
        default_version,
        description=None,
        terms_of_service=None,
        contact=None,
        license=None,
        doc="docs/",
        redoc="redoc/",
        **extra
    ):
        schema_view = get_schema_view(
            info=openapi.Info(
                title=title,
                default_version=default_version,
                description=description,
                terms_of_service=terms_of_service,
                contact=contact,
                license=license,
            ),
            url=self.url,
            patterns=None,
            urlconf=None,
            public=self.public,  # 使用实例的 public 参数，而不是硬编码 False
            validators=self.validators,
            generator_class=self.generator_class,
            authentication_classes=self.authentication_classes,
            permission_classes=self.permission_classes,
        )
        return (
            re_path(
                r"^%s(?P<format>\.json|\.yaml)$" % (doc), schema_view.without_ui(cache_timeout=0), name="schema-json"
            ),
            path(doc, schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
            path(redoc, schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
        )


class Form(openapi.Parameter):
    def __init__(
        self,
        name,
        description=None,
        required=None,
        schema=None,
        type=None,
        format=None,
        enum=None,
        pattern=None,
        items=None,
        default=None,
        **extra
    ):
        super(Form, self).__init__(
            name=name,
            in_=openapi.IN_FORM,
            description=description,
            required=required,
            schema=schema,
            type=type,
            format=format,
            enum=enum,
            pattern=pattern,
            items=items,
            default=default,
            **extra
        )


class File(openapi.Parameter):
    def __init__(
        self,
        name="file",
        description=None,
        required=None,
        schema=None,
        format=None,
        enum=None,
        pattern=None,
        items=None,
        default=None,
        **extra
    ):
        super(File, self).__init__(
            name=name,
            in_=openapi.IN_FORM,
            description=description,
            required=required,
            schema=schema,
            type=openapi.TYPE_FILE,
            format=format,
            enum=enum,
            pattern=pattern,
            items=items,
            default=default,
            **extra
        )


class Body(openapi.Parameter):
    def __init__(
        self,
        name,
        description=None,
        required=None,
        schema=None,
        type=None,
        format=None,
        enum=None,
        pattern=None,
        items=None,
        default=None,
        **extra
    ):
        super(Body, self).__init__(
            name=name,
            in_=openapi.IN_BODY,
            description=description,
            required=required,
            schema=schema,
            type=type,
            format=format,
            enum=enum,
            pattern=pattern,
            items=items,
            default=default,
            **extra
        )


class Path(openapi.Parameter):
    def __init__(
        self,
        name,
        description=None,
        required=None,
        schema=None,
        type=None,
        format=None,
        enum=None,
        pattern=None,
        items=None,
        default=None,
        **extra
    ):
        super(Path, self).__init__(
            name=name,
            in_=openapi.IN_PATH,
            description=description,
            required=required,
            schema=schema,
            type=type,
            format=format,
            enum=enum,
            pattern=pattern,
            items=items,
            default=default,
            **extra
        )


class Query(openapi.Parameter):
    def __init__(
        self,
        name,
        description=None,
        required=None,
        schema=None,
        type=None,
        format=None,
        enum=None,
        pattern=None,
        items=None,
        default=None,
        **extra
    ):
        super(Query, self).__init__(
            name=name,
            in_=openapi.IN_QUERY,
            description=description,
            required=required,
            schema=schema,
            type=type,
            format=format,
            enum=enum,
            pattern=pattern,
            items=items,
            default=default,
            **extra
        )


class Header(openapi.Parameter):
    def __init__(
        self,
        name,
        description=None,
        required=None,
        schema=None,
        type=None,
        format=None,
        enum=None,
        pattern=None,
        items=None,
        default=None,
        **extra
    ):
        super(Header, self).__init__(
            name=name,
            in_=openapi.IN_HEADER,
            description=description,
            required=required,
            schema=schema,
            type=type,
            format=format,
            enum=enum,
            pattern=pattern,
            items=items,
            default=default,
            **extra
        )


class StandardPageNumberPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    page_size = 10
    max_page_size = 1000


class MultipartView(APIView):
    parser_classes = (MultiPartParser,)


class FormView(CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
