from django.db import models
from django.conf import settings
import secrets


class TokenModel(models.Model):
    id = models.AutoField(primary_key=True)  # 数据库自增主键
    key = models.CharField(max_length=40, unique=True, editable=False, db_index=True)  # token字符串，唯一且有索引
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='token',
        on_delete=models.CASCADE,
        editable=False
    )
    rate = models.IntegerField(help_text="速率", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.key:
            # 自动生成40位的安全token
            self.key = secrets.token_hex(20)  # 生成40个字符的十六进制token
        super().save(*args, **kwargs)

    @classmethod
    def get(cls, user, token):
        # use cache if possible
        return cls.objects.get(user=user, key=token)  # 修正参数名

    class Meta:
        pass

