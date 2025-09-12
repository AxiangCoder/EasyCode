from rest_framework import serializers
from .models import User

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'id',  'avatar', 'role', 'is_active', 'is_superuser', 'is_delete', 'created_time', 'updated_time', 'username']
        # read_only_fields = ['id', 'created_time', 'updated_time']
        read_only_fields = ['id',  'avatar', 'role', 'is_active', 'is_superuser', 'is_delete', 'created_time', 'updated_time', 'username']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.password = validated_data.get('password', instance.password)
        instance.save()
        return instance
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'id', 'username']
        # read_only_fields = ['id', 'created_time', 'updated_time']
        read_only_fields = ['id', 'email', 'password', 'id', 'username']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()