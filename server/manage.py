#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

admin_py = """
from django.contrib import admin

# Register your models here.
"""

filters_py = """
import django_filters
from .models import ProjectModel

class ProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = ProjectModel
        fields = "__all__"

"""

models_py = """
from django.db import models
from utils import EnumDesc

class ProjectModel(models.Model):
    name = models.CharField(max_length=255)
"""

serializers_py = """
from rest_framework import serializers
from .models import ProjectModel

class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectModel
        fields = "__all__"
        depth = 0
"""

urls_py = """
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers
from .views import ProjectViewSet

router = routers.DefaultRouter()
router.register(r"", ProjectViewSet)

urlpatterns = [
    path("", include(router.urls)),
]


"""

views_py = """
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
from .models import ProjectModel
from .serializers import ProjectSerializer


# Create your views here.


_tag = "Project"


@method_decorator(name="create",
                  decorator=swagger_view.swagger_auto_schema(operation_summary=f"导入{_tag}", tags=[_tag]))
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
class ProjectViewSet(viewsets.ModelViewSet):
    model_class = ProjectModel
    queryset = model_class.objects.all().filter()
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_class = []
    order_fields = []

"""


def create_app(name):
    import inflection
    if os.path.exists(os.path.join("apps", name)):
        print(f"app {name} already exists")
        return
    os.makedirs(os.path.join("apps", name), exist_ok=True)
    os.makedirs(os.path.join("apps", name, "migrations"), exist_ok=True)
    project = inflection.camelize(name)
    with open(os.path.join("apps", name, "__init__.py"), "w") as f:
        f.write("")
    with open(os.path.join("apps", name, "migrations", "__init__.py"), "w") as f:
        f.write("")
    with open(os.path.join("apps", name, "models.py"), "w") as f:
        f.write(models_py.replace("Project", project))
    with open(os.path.join("apps", name, "serializers.py"), "w") as f:
        f.write(serializers_py.replace("Project", project))
    with open(os.path.join("apps", name, "views.py"), "w") as f:
        f.write(views_py.replace("Project", project))
    with open(os.path.join("apps", name, "urls.py"), "w") as f:
        f.write(urls_py.replace("Project", project))
    with open(os.path.join("apps", name, "admin.py"), "w") as f:
        f.write(admin_py.replace("Project", project))
    with open(os.path.join("apps", name, "filters.py"), "w") as f:
        f.write(filters_py.replace("Project", project))


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    if sys.argv[1] == "create_app":
        name = sys.argv[2]
        create_app(name)
    else:
        main()
