from django.db import models
from django.contrib.auth.models import AbstractUser

from foodgram import settings


class CustomUser(AbstractUser):
    username = models.CharField(
        unique=True,
        verbose_name='Имя пользователя',
        max_length=settings.MAX_LEN_USERS_CHARFIELD,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=settings.MAX_LEN_USERS_CHARFIELD,
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        max_length=settings.MAX_LEN_EMAIL_FIELD,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.MAX_LEN_USERS_CHARFIELD,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.MAX_LEN_USERS_CHARFIELD,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'{self.username}/{self.email}'


class Subscribe(models.Model):
    subscriber = models.ForeignKey(
        CustomUser,
        related_name='subscriber',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='subscribing',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                name='unique_subscription',
                fields=['subscriber', 'author'],
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
