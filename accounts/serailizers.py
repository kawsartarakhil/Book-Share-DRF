from rest_framework import serializers
from .models import CustomUser

class RegisterSerailizer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["id","username","email","password","password2"]

    def validate_email(self,value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate(self,data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self,validated_data):
        validated_data.pop("password2")
        user = CustomUser.objects.create_user(**validated_data)
        return user


class Loginserailizer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username","password"]

class LogoutSerailizer(serializers.Serializer):
    refresh = serializers.CharField()

class RefreshSerailizer(serializers.Serializer):
    refresh = serializers.CharField()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id","username","email","city","phone_number"]
        read_only_fields = ["id","username","email"]
