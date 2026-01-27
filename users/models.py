from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Кастомная модель пользователя с email как основным полем"""

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to.'),
        related_name="custom_user_set",  # Уникальное имя
        related_query_name="custom_user",
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_set",  # Уникальное имя
        related_query_name="custom_user",
    )

    # Делаем email обязательным и уникальным
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. Enter a valid email address.')
    )

    # Дополнительные поля (по заданию)
    avatar = models.ImageField(
        _('avatar'),
        upload_to='users/avatars/',
        blank=True,
        null=True,
        help_text=_('Upload your profile picture')
    )

    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Enter your phone number')
    )

    country = models.CharField(
        _('country'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Enter your country')
    )

    # Указываем что email - поле для авторизации
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Для createsuperuser

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """Автоматически создаем username из email если не указан"""
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)