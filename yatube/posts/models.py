from django.contrib.auth import get_user_model
from django.db import models

from yatube.settings import FIRST_CHARACTERS

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
    )
    slug = models.SlugField(
        unique=True,
    )
    description = models.TextField(
        verbose_name='Описание группы',
    )

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст сообщения',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:FIRST_CHARACTERS]
