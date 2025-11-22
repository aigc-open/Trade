#!/usr/bin/env python
"""
检查 Token 是否有效的脚本
Usage: python check_token.py <token>
"""
import os
import sys
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.authtoken.models import Token
from apps.user.models import UserModel


def check_token(token_key):
    """检查 Token 是否有效"""
    try:
        token = Token.objects.get(key=token_key)
        user = token.user
        
        print(f"✅ Token 有效！")
        print(f"\n📋 Token 信息:")
        print(f"   Token: {token.key}")
        print(f"   用户: {user.username}")
        print(f"   用户ID: {user.id}")
        print(f"   邮箱: {user.email or '(未设置)'}")
        print(f"   角色: {user.get_role_display()}")
        print(f"   状态: {user.get_status_display()}")
        print(f"   是否激活: {'是' if user.is_active else '否'}")
        print(f"   是否员工: {'是' if user.is_staff else '否'}")
        print(f"   是否超级用户: {'是' if user.is_superuser else '否'}")
        
        # 检查用户状态
        if user.status != 'active':
            print(f"\n⚠️  警告: 用户状态为 '{user.get_status_display()}'，可能无法使用 API")
        
        if not user.is_active:
            print(f"\n⚠️  警告: 用户未激活，无法使用 API")
        
        # 测试 curl 命令
        print(f"\n🧪 测试 curl 命令:")
        print(f'   curl -H "Authorization: Token {token.key}" http://localhost:8000/api/v1/analytics/dashboard/')
        
        return True
        
    except Token.DoesNotExist:
        print(f"❌ Token 无效: {token_key}")
        print(f"\n💡 可能的原因:")
        print(f"   1. Token 不存在")
        print(f"   2. Token 已被删除")
        print(f"   3. Token 格式错误")
        print(f"\n💡 解决方案:")
        print(f"   python get_token.py <username>  # 获取或创建 Token")
        return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def list_all_tokens():
    """列出所有 Token"""
    print("📋 数据库中的所有 Token:")
    print("-" * 100)
    
    tokens = Token.objects.select_related('user').all()
    if not tokens:
        print("（数据库中暂无 Token）")
        print("\n💡 创建 Token:")
        print("   python get_token.py <username>")
        return
    
    for token in tokens:
        user = token.user
        status = "✅" if user.is_active and user.status == 'active' else "⚠️ "
        print(f"{status} {user.username:15} | {user.get_role_display():10} | {token.key}")
    
    print("-" * 100)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("🔍 Token 验证工具\n")
        print("用法:")
        print("  python check_token.py <token>     # 检查指定 Token")
        print("  python check_token.py --list      # 列出所有 Token")
        print("\n示例:")
        print("  python check_token.py 3a31f955dc1169524ed2d574733a8bc314f9d028")
        print()
        list_all_tokens()
        sys.exit(0)
    
    token_key = sys.argv[1]
    
    if token_key in ['--list', '--all']:
        list_all_tokens()
    else:
        check_token(token_key)


if __name__ == '__main__':
    main()

