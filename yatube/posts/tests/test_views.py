from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from yatube.settings import POSTS_COUNT, POSTS_TEST_COUNT

COUNT_FOR_POSTS = 14


class PostPagesTest(TestCase):
    """Тестрование страниц приложения posts на корректную
    работу views-функций."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        User = get_user_model()
        cls.test_user1 = User.objects.create(username='NoName')
        cls.ok_group = Group.objects.create(
            title='Правильная тестовая группа',
            slug='ok-slug',
            description='Описание правильной группы',
        )
        cls.wrong_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='wrong-slug',
            description='Описание другой группы',
        )
        cls.test_post = Post.objects.create(
            text='Тестовое сообщение!!!',
            author=cls.test_user1,
            group=cls.ok_group,
        )

    def setUp(self):
        """ Создание неавторизованного клиента и
        клиента с авторизованным пользователем."""
        self.guest_client = Client()

        user1 = get_user_model()
        self.user1 = user1.objects.get(username='NoName')
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)

        user2 = get_user_model()
        self.user2 = user2.objects.create(username='TestUser2')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        page_templates_dict = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.ok_group.slug},
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.test_post.author},
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.test_post.id},
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.test_post.id},
            ): 'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
        }

        for reverse_name, template in page_templates_dict.items():
            with self.subTest(template=template):
                response = self.authorized_client1.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """View-функция страницы index передает правильный контекст."""
        response = self.authorized_client1.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post, self.test_post)

    def test_group_list_page_show_correct_context(self):
        """View-функция страницы group_list передает правильный контекст."""
        response = self.authorized_client1.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.ok_group.slug},
        ))
        test_group_field = response.context.get('group')
        self.assertEqual(test_group_field, self.ok_group)

    def test_post_create_page_show_correct_context(self):
        """View-функция страницы post_create передает правильный контекст."""
        response = self.authorized_client1.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for field_name, field_format in form_fields.items():
            with self.subTest(value=field_name):
                form_field = (
                    response.context.get('form').fields.get(field_name)
                )
                self.assertIsInstance(form_field, field_format)

    def test_profile_page_show_correct_context(self):
        """View-функция страницы профайла передает правильный контекст."""
        response = self.authorized_client2.get(reverse(
            'posts:profile',
            kwargs={'username': self.test_post.author},
        ))
        test_profile_field = response.context.get('page_obj')[0]
        self.assertEqual(test_profile_field, self.test_post)

    def test_post_detail_show_correct_context(self):
        """View-функция страницы поста передает правильный контекст."""
        response = self.authorized_client2.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.test_post.id},
        ))
        post_detail_field = response.context.get('post')
        self.assertEqual(post_detail_field, self.test_post)

    def test_post_edit_page_show_correct_context(self):
        """View-функция редактирования поста передает правильный контекст."""
        response = self.authorized_client1.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.test_post.id},
            ),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for field_name, field_format in form_fields.items():
            with self.subTest(value=field_name):
                form_field = (
                    response.context.get('form').fields.get(field_name)
                )
                self.assertIsInstance(form_field, field_format)

    def test_post_in_right_group(self):
        """Пост попал в нужную группу"""
        groups_list = {
            'ok_group': reverse(
                'posts:group_list',
                kwargs={'slug': self.ok_group.slug},
            ),
            'wrong_group': reverse(
                'posts:group_list',
                kwargs={'slug': self.wrong_group.slug}
            )
        }
        for some_group, reverse_name in groups_list.items():
            with self.subTest():
                response = self.authorized_client1.get(reverse_name)
                posts_in_group = response.context.get('page_obj')
                if some_group == 'ok_group':
                    self.assertIn(self.test_post, posts_in_group)
                else:
                    self.assertNotIn(self.test_post, posts_in_group)

    def test_main_page_display_post(self):
        """Пост видно на главной странице"""
        response = self.authorized_client1.get(reverse('posts:index'))
        main_page_view = response.context.get('page_obj')
        self.assertIn(self.test_post, main_page_view)

    def test_profile_page_display_post(self):
        """Пост видно на странице автора"""
        response = self.authorized_client1.get(reverse(
            'posts:profile',
            kwargs={'username': self.test_post.author},
        ))
        profile_page_view = response.context.get('page_obj')
        self.assertIn(self.test_post, profile_page_view)


class PaginatorViewsTest(TestCase):
    """Тестирование страниц на корректную работу паджинатора."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        User = get_user_model()
        cls.test_user1 = User.objects.create(username='TestUser1')
        cls.group = Group.objects.create(
            title='Tестовая группа',
            slug='ok-slug',
            description='Описание группы',
        )
        cls.test_posts = []
        for post in range(1, COUNT_FOR_POSTS):
            cls.test_posts.append(Post(
                text=f'Тестовое сообщение - {post}',
                author=cls.test_user1,
                group=cls.group,
            ))
        Post.objects.bulk_create(cls.test_posts)

    def setUp(self):
        self.index_reverse = reverse('posts:index')
        self.group_list_reverse = reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}
        )
        self.profile_reverse = reverse(
            'posts:profile',
            kwargs={'username': self.test_user1}
        )

    def test_first_page_urls_contains_ten_records(self):
        """Проверка: количество постов на странице равно 10."""
        url_reverse_list = [
            self.index_reverse,
            self.group_list_reverse,
            self.profile_reverse,
        ]
        for url_reverse in url_reverse_list:
            with self.subTest(url_reverse=url_reverse):
                response = self.client.get(url_reverse)
                self.assertEqual(
                    len(response.context['page_obj']),
                    POSTS_COUNT,
                )

    def test_second_page_urls_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста."""
        url_reverse_list = [
            self.index_reverse,
            self.group_list_reverse,
            self.profile_reverse,
        ]
        for url_reverse in url_reverse_list:
            with self.subTest(url_reverse=url_reverse):
                response = self.client.get(url_reverse + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    POSTS_TEST_COUNT,
                )
