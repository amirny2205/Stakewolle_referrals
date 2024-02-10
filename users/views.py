'''
I have overriden many methods for swagger to capture it correctly
'''
from djoser.views import UserViewSet
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from djoser.conf import settings
from django.utils import timezone
from django.http import HttpResponseBadRequest
from rest_framework.response import Response
from .models import ReferralCode
from . import serializers
from djoser.serializers import UserSerializer
from django.core.mail import send_mail
from django.conf import settings as project_settings
from rest_framework import viewsets, status
from drf_spectacular.utils import extend_schema


User = get_user_model()


def es(view):
    '''exclude_schema exclude short version'''
    return extend_schema(exclude=True)(view)


class UserViewSetUpdated(UserViewSet):
    serializer_class = settings.SERIALIZERS.user
    queryset = User.objects.all()
    permission_classes = settings.PERMISSIONS.user
    token_generator = default_token_generator
    lookup_field = settings.USER_ID_FIELD

    def create(self, request, *args, **kwargs):
        '''Create user'''
        serializer = serializers.UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if 'referral_code_for_registration' in serializer.validated_data:
            if serializer.validated_data['referral_code_for_registration'].\
               active is False:
                return HttpResponseBadRequest("Error: referral code is not active")
            if serializer.validated_data['referral_code_for_registration'].\
               expiry_date < timezone.now():
                return HttpResponseBadRequest("Error: referral code expired")
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)

    @es
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @es
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @es
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @es
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @es
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @es
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @es
    def activation(self, request, *args, **kwargs):
        return super().activation(request, *args, **kwargs)

    @es
    def resend_activation(self, request, *args, **kwargs):
        return super().resend_activation(request, *args, **kwargs)

    @es
    def set_password(self, request, *args, **kwargs):
        return super().set_password(request, *args, **kwargs)

    @es
    def reset_password(self, request, *args, **kwargs):
        return super().reset_password(request, *args, **kwargs)

    @es
    def reset_password_confirm(self, request, *args, **kwargs):
        return super().reset_password_confirm(request, *args, **kwargs)

    @es
    def set_username(self, request, *args, **kwargs):
        return super().set_username(request, *args, **kwargs)

    @es
    def reset_username(self, request, *args, **kwargs):
        return super().reset_username(request, *args, **kwargs)

    @es
    def reset_username_confirm(self, request, *args, **kwargs):
        return super().reset_username_confirm(request, *args, **kwargs)


class ReferralCodeViewSet(viewsets.ModelViewSet):
    queryset = ReferralCode.objects.all()
    serializer_class = serializers.ReferralCodeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset

    @extend_schema(
        request=serializers.ReferralCodeViewSetSwaggerSerializerCreate,
    )
    def create(self, request, *args, **kwargs):
        '''Create new referral code'''
        request.data['user'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        if 'send_mail' in request.data.keys() and \
           request.data['send_mail'] is True:
            if request.user.email == "":
                return HttpResponseBadRequest("User doesn't have email")
            if project_settings.EMAIL_HOST_USER == '' or \
               project_settings.EMAIL_HOST_USER == '':
                return HttpResponseBadRequest(
                    ".env has incorrect EMAIL_HOST_USER or EMAIL_HOST_USER")
            send_mail(
                "Your referral code",
                serializer.data['code_str'],
                project_settings.EMAIL_HOST_USER,
                [request.user.email],
                fail_silently=False,
            )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        '''Get referral codes that current user owns'''
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        '''Retrieve a single code by it's code_str'''
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        request=serializers.ReferralCodeViewSetSwaggerSerializerUpdate,
    )
    def update(self, request, *args, **kwargs):
        '''Fully update a referral code instance'''
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        '''Partially update a referral code instance'''
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        '''Delete a referral code instance'''
        return super().destroy(request, *args, **kwargs)


class ReferralsViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        new_queryset = []
        if 'id' not in self.request.data.keys():
            return []
        user = User.objects.get(pk=self.request.data['id'])
        rcs = user.referral_code_set.all()
        for obj in queryset:
            if obj.referral_code_for_registration is not None \
               and obj.referral_code_for_registration in rcs:
                new_queryset.append(obj)
        return new_queryset

    @es
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=serializers.ReferralsViewSetSwaggerSerializerCreate,
    )
    def create(self, request, *args, **kwargs):
        '''Get a list of users that used any of your referral codes'''
        if 'id' not in self.request.data.keys():
            return HttpResponseBadRequest(
                    "please include user 'id' in body")

        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    @es
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @es
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @es
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @es
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
