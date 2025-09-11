from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'phone', 'password')
        # extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
            user = User.objects.create_user(
                email=validated_data['email'],
                phone=validated_data['phone'],
                password=validated_data['password'],
            )
            return user

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=False)
    password = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    phone = serializers.CharField(max_length=11, required=False, allow_blank=True)
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')
        if not (email or password):
            raise serializers.ValidationError('邮箱或电话号码必须填写一个')

        user = None
        if email:
            user = User.objects.get(email=email)
            if not user:
                raise (serializers.ValidationError('邮箱错误'))
            if not user.check_password(password):
                raise (serializers.ValidationError('密码错误'))
        if phone:
            user = User.objects.get(phone=phone)
            if not user:
                raise (serializers.ValidationError('电话号码错误'))
            if not user.check_password(password):
                raise (serializers.ValidationError('密码错误'))
        return user



