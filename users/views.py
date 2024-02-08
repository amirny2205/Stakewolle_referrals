from djoser.views import UserViewSet
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from djoser.conf import settings
from django.utils import timezone
from django.http import HttpResponseBadRequest
from rest_framework import status, mixins
from rest_framework.response import Response
from .models import ReferralCode
from .serializers import ReferralCodeSerializer
from rest_framework import generics
from djoser.serializers import UserSerializer
from django.core.mail import send_mail
from django.conf import settings as project_settings

User = get_user_model()


class UserViewSetUpdated(UserViewSet):
    serializer_class = settings.SERIALIZERS.user
    queryset = User.objects.all()
    permission_classes = settings.PERMISSIONS.user
    token_generator = default_token_generator
    lookup_field = settings.USER_ID_FIELD

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['referral_code_for_registration'].\
           expiry_date < timezone.now():
            return HttpResponseBadRequest("Error: referral code expired")
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)


class ReferralCodeList(generics.ListCreateAPIView):
    queryset = ReferralCode.objects.all()
    serializer_class = ReferralCodeSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        if 'send_mail' in request.data.keys() and \
           request.data['send_mail'] == True:
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

    
class ReferralCodeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReferralCode.objects.all()
    serializer_class = ReferralCodeSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset


class GetReferrals(mixins.ListModelMixin,
                   generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        new_queryset = []
        rcs = self.request.user.referral_code_set.all()
        for obj in queryset:
            if obj.referral_code_for_registration is not None \
               and obj.referral_code_for_registration in rcs:
                new_queryset.append(obj)
        return new_queryset
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
