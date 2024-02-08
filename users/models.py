from django.db import models
from django.contrib.auth.models import User
import random


class ReferralCode(models.Model):
    code_str = models.CharField(max_length=64,
                                primary_key=True,
                                default=lambda: "".join(
                                    [chr(random.randrange(48, 123))
                                     for y in range(64)]))
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
