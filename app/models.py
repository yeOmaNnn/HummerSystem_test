import random
import string

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from app.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    invite_code = models.CharField(max_length=20, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(max_length=20, blank=True, validators=[phone_regex])
    is_active = models.BooleanField(_('active'), default=False)
    is_staff = models.BooleanField(_('staff'), default=False)

    is_verified = models.BooleanField(_('verified'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class RefUser(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_given')
    who_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_received')

    def __str__(self):
        return f"{self.user_id} - {self.who_user_id}"

    class Meta:
        verbose_name = _("RefUser")
        verbose_name_plural = _('RefUser')

@receiver(pre_save, sender=RefUser)
def check_referral_users(sender, instance, **kwargs):
    if instance.user_id == instance.who_user_id:
        raise ValueError("User can`t invite himself.")
    if RefUser.objects.filter(who_user_id=instance.who_user_id).exists():
        raise ValueError("User already invite!")


@receiver(post_save, sender=User)
def generate_invite_code(sender, instance, created, **kwargs):
    if created and not instance.invite_code:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        instance.invite_code = code
        instance.save()
