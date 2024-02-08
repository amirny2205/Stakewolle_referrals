from djoser.views import UserViewSet
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from djoser.conf import settings
from django.utils import timezone
from django.http import HttpResponseBadRequest
from rest_framework import status
from rest_framework.response import Response

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
