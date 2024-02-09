from .models import ReferralCode
from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = '__all__'


class ReferralCodeViewsetSwaggerSerializerCreate(serializers.ModelSerializer):
    active = serializers.BooleanField(default=False)
    expiry_date = serializers.DateTimeField(required=True)
    send_email = serializers.BooleanField(default=False)

    class Meta:
        model = ReferralCode
        fields = ["expiry_date", "active", "send_email"]


class ReferralCodeViewsetSwaggerSerializerUpdate(serializers.ModelSerializer):
    active = serializers.BooleanField(required=True)
    expiry_date = serializers.DateTimeField(required=True)
    user = serializers.IntegerField(required=True)
    code_str = serializers.CharField(required=True)

    class Meta:
        model = ReferralCode
        fields = ["expiry_date", "active", "user", "code_str"]
