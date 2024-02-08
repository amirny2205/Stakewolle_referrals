from djoser.serializers import \
    UserCreateSerializer as BaseUserRegistrationSerializer
from .models import ReferralCode
from rest_framework import serializers


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = '__all__'


class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = '__all__'
