
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import UserModel


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'is_staff', 'is_superuser', 'date_joined', 'created_at', 
                 'updated_at', 'password']
        read_only_fields = ['id', 'date_joined', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserModel(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('用户名或密码错误')
            if not user.is_active:
                raise serializers.ValidationError('用户账户已被禁用')
            data['user'] = user
        else:
            raise serializers.ValidationError('必须提供用户名和密码')
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器（管理员账号）"""
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'date_joined', 'created_at', 'updated_at']
        read_only_fields = ['id', 'username', 'date_joined', 'created_at', 'updated_at']
        ref_name = 'AdminUserProfile'  # 设置唯一的 ref_name
    


