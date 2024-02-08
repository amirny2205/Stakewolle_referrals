from django.db import models
from django.contrib.auth.models import AbstractUser
import random


def generate_random_code():
    return "".join([chr(random.randrange(48, 123)) for y in range(64)])


class ReferralCode(models.Model):
    code_str = models.CharField(max_length=64,
                                primary_key=True,
                                default=generate_random_code)
    active = models.BooleanField(default=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE,
                             related_name="user_set")
    expiry_date = models.DateTimeField()

    def __str__(self):
        return self.code_str


class User(AbstractUser):
    referral_code_for_registration = models.ForeignKey(
        ReferralCode, on_delete=models.CASCADE,
        related_name="referral_code_set",
        null=True, blank=True)
