from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        User = get_user_model()
        cls.user = User.objects.create(username='NoName')

        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.test_post = Post.objects.create(
            text='Тестовое сообщение!!!',
            author=cls.user,
            group=cls.test_group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Другое сообщение!!!',
            'group': self.test_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user},
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.test_group,
                text='Другое сообщение!!!',
                author=self.user,
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма редактирует существующую запись в Post."""
        posts_count = Post.objects.count()
        edit_post = PostFormTests.test_post
        form_new_data = {
            'text': 'Новый текст',
            'author': self.user,
            'group': self.test_group.id,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': edit_post.id},
            ),
            data=form_new_data,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': edit_post.id},
        ))

        self.assertEqual(Post.objects.count(), posts_count)
        new_post = Post.objects.last()
        self.assertTrue(new_post)
        self.assertEqual(new_post.text, form_new_data['text'])
        self.assertEqual(new_post.author, form_new_data['author'])
        self.assertEqual(new_post.group.id, form_new_data['group'])
