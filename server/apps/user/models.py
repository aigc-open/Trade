from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token
from django.conf import settings

class UserModel(AbstractUser):
    """
    管理员用户模型
    扩展Django默认User模型，添加角色、状态等字段
    """
    # 管理员角色
    ROLE_CHOICES = [
        ('super_admin', '超级管理员'),
        ('operator', '运营管理员'),
        ('devops', '运维管理员'),
    ]
    
    # 账号状态
    STATUS_CHOICES = [
        ('active', '正常'),
        ('disabled', '禁用'),
        ('locked', '锁定'),
    ]
    
    # 扩展字段
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='operator',
        verbose_name='角色',
        help_text='管理员角色（超级管理员/运营管理员/运维管理员）'
    )
    real_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='真实姓名'
    )
    mobile = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='手机号'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='账号状态'
    )
    
    # 登录相关
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='最后登录IP'
    )
    login_fail_count = models.IntegerField(
        default=0,
        verbose_name='连续登录失败次数'
    )
    lock_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='锁定截止时间'
    )
    
    # 创建信息
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        verbose_name='创建人'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        null=True,
        help_text="创建时间"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        null=True,
        help_text="更新时间"
    )
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='usermodel_set',
        related_query_name='usermodel',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='usermodel_set',
        related_query_name='usermodel',
    )
    session_key = models.CharField(max_length=256, default=None, null=True)

    class Meta:
        db_table = "user"
        ordering = ["-date_joined"]
        verbose_name = "管理员"
        verbose_name_plural = "管理员"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_super_admin(self):
        """是否是超级管理员"""
        return self.role == 'super_admin'
    
    def is_operator(self):
        """是否是运营管理员"""
        return self.role == 'operator'
    
    def is_devops(self):
        """是否是运维管理员"""
        return self.role == 'devops'


class LoginLog(models.Model):
    """
    登录日志模型
    记录所有管理员的登录历史
    """
    # 登录状态
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
    ]
    
    # 失败原因
    FAIL_REASON_CHOICES = [
        ('invalid_username', '用户名不存在'),
        ('invalid_password', '密码错误'),
        ('account_disabled', '账号已禁用'),
        ('account_locked', '账号已锁定'),
        ('too_many_attempts', '登录尝试次数过多'),
        ('other', '其他原因'),
    ]
    
    # 基本信息
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='login_logs',
        verbose_name='用户'
    )
    username = models.CharField(
        max_length=150,
        verbose_name='用户名'
    )
    
    # 登录信息
    login_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name='登录状态'
    )
    fail_reason = models.CharField(
        max_length=50,
        choices=FAIL_REASON_CHOICES,
        null=True,
        blank=True,
        verbose_name='失败原因'
    )
    
    # 客户端信息
    ip_address = models.GenericIPAddressField(
        verbose_name='登录IP'
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name='User-Agent'
    )
    location = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='地理位置'
    )
    
    # 时间信息
    login_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='登录时间'
    )
    
    class Meta:
        db_table = 'login_logs'
        verbose_name = '登录日志'
        verbose_name_plural = '登录日志'
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', '-login_time']),
            models.Index(fields=['username', '-login_time']),
            models.Index(fields=['login_status', '-login_time']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.get_login_status_display()} - {self.login_time}"