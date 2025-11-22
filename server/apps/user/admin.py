"""
User Admin - 管理员管理后台
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserModel, LoginLog


@admin.register(UserModel)
class UserModelAdmin(UserAdmin):
    """管理员用户管理"""
    list_display = [
        'username', 'real_name', 'email', 'role', 'status',
        'last_login', 'last_login_ip', 'is_active'
    ]
    list_filter = ['role', 'status', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'real_name', 'email', 'mobile']
    readonly_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'password', 'real_name', 'email', 'mobile')
        }),
        ('权限设置', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('状态信息', {
            'fields': ('status', 'login_fail_count', 'lock_until')
        }),
        ('登录信息', {
            'fields': ('last_login', 'last_login_ip', 'date_joined')
        }),
        ('创建信息', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'real_name', 'email', 'mobile', 'role'),
        }),
    )


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    """登录日志管理"""
    list_display = [
        'username', 'login_status', 'fail_reason',
        'ip_address', 'location', 'login_time'
    ]
    list_filter = ['login_status', 'fail_reason', 'login_time']
    search_fields = ['username', 'ip_address']
    readonly_fields = ['login_time']
    date_hierarchy = 'login_time'
    ordering = ['-login_time']
    
    def has_add_permission(self, request):
        # 登录日志由系统自动创建
        return False
    
    def has_change_permission(self, request, obj=None):
        # 登录日志不允许修改
        return False
