#!/usr/bin/env python
"""
快速获取用户 Token 的脚本
Usage: python get_token.py [username]
"""
import os
import sys
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.authtoken.models import Token
from apps.user.models import UserModel


def get_or_create_token(username):
    """获取或创建用户的 Token"""
    try:
        user = UserModel.objects.get(username=username)
        token, created = Token.objects.get_or_create(user=user)
        
        if created:
            print(f"✅ 为用户 '{username}' 创建了新的 Token")
        else:
            print(f"✅ 用户 '{username}' 的 Token 已存在")
        
        print(f"\n📋 Token 信息:")
        print(f"   Token: {token.key}")
        print(f"   用户: {user.username}")
        print(f"   角色: {user.get_role_display()}")
        print(f"   状态: {user.get_status_display()}")
        
        print(f"\n🔐 在 Swagger 中使用:")
        print(f"   Token {token.key}")
        
        print(f"\n📝 在 curl 中使用:")
        print(f"   curl -H \"Authorization: Token {token.key}\" http://localhost:8000/api/v1/analytics/dashboard/")
        
        return token.key
        
    except UserModel.DoesNotExist:
        print(f"❌ 错误: 用户 '{username}' 不存在")
        print(f"\n💡 可用的用户列表:")
        users = UserModel.objects.all()
        if users:
            for u in users:
                print(f"   - {u.username} ({u.get_role_display()})")
        else:
            print(f"   （暂无用户，请先创建：python manage.py createsuperuser）")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        sys.exit(1)


def list_all_tokens():
    """列出所有用户的 Token"""
    print("📋 所有用户的 Token:")
    print("-" * 80)
    
    tokens = Token.objects.select_related('user').all()
    if not tokens:
        print("（暂无 Token，使用 'python get_token.py <username>' 创建）")
        return
    
    for token in tokens:
        user = token.user
        print(f"用户: {user.username:15} | 角色: {user.get_role_display():10} | Token: {token.key}")
    
    print("-" * 80)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("🔑 DataTraceHub Token 管理工具\n")
        print("用法:")
        print("  python get_token.py <username>   # 获取指定用户的 Token")
        print("  python get_token.py --list       # 列出所有用户的 Token")
        print("  python get_token.py --all        # 列出所有用户的 Token")
        print("\n示例:")
        print("  python get_token.py admin")
        print()
        
        # 显示可用用户
        users = UserModel.objects.all()
        if users:
            print("💡 可用的用户:")
            for u in users:
                print(f"   - {u.username} ({u.get_role_display()})")
        else:
            print("💡 暂无用户，请先创建：")
            print("   python manage.py createsuperuser")
        sys.exit(0)
    
    username = sys.argv[1]
    
    if username in ['--list', '--all']:
        list_all_tokens()
    else:
        get_or_create_token(username)


if __name__ == '__main__':
    main()

