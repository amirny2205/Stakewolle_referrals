from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Q, UniqueConstraint
import random
import string


def generate_random_code():
    letters = string.ascii_lowercase
    return "".join([random.choice(letters) for y in range(64)])


class ReferralCode(models.Model):
    code_str = models.CharField(max_length=64,
                                primary_key=True,
                                default=generate_random_code)
    active = models.BooleanField(default=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             related_name="referral_code_set")
    expiry_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.active:
            ReferralCode.objects.filter(user=self.user, active=True).exclude(
                pk=self.pk
            ).update(active=False)
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "active"],
                condition=Q(active=True),
                name="unique_active_code_for_user",
            )
        ]

    def __str__(self):
        return self.code_str


class User(AbstractUser):
    referral_code_for_registration = models.ForeignKey(
        ReferralCode, on_delete=models.SET_NULL,
        related_name="user_set",
        null=True, blank=True)
