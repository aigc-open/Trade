"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import path, include, re_path
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.documentation import include_docs_urls
import apps.urls
from utils.djSwagger import swagger_view, permission_auth


def root(request):
    return redirect("/docs/")

swagger = swagger_view.SwaggerConfig(public=True)
############################# 路由注册 #############################

urlpatterns = [
    *tuple(apps.urls.urlpatterns),
    *swagger.paths(title="后端 API",
                   default_version='v1.0',
                   description="接口文档"),
    re_path(r'^$', root, name='root')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
