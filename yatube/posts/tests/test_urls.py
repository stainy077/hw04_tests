from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

START_PAGE = '/'
NEW_POST_PAGE = '/create/'


class PostURLTests(TestCase):
    """Тесты доступности страниц."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        User = get_user_model()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовое сообщение!!!',
            author=User.objects.create(username='NoName'),
            group=cls.group,
        )
        user1 = get_user_model()
        cls.user1 = user1.objects.get(username='NoName')
        cls.authorized_client1 = Client()
        cls.authorized_client1.force_login(cls.user1)

        user2 = get_user_model()
        cls.user2 = user2.objects.create(username='TestUser')
        cls.authorized_client2 = Client()
        cls.authorized_client2.force_login(cls.user2)

    def setUp(self):
        """Создание клиентов."""
        self.guest_client = Client()

        self.group_page = f'/group/{self.group.slug}/'
        self.profile_page = f'/profile/{self.post.author}/'
        self.post_detail_page = f'/posts/{self.post.id}/'
        self.post_edit_page = f'/posts/{self.post.id}/edit/'

    def test_urls_exists_at_desired_location_anonymous(self):
        """Проверка доступности URL-адреса неавторизованым пользователям."""
        url_list = [
            START_PAGE,
            self.group_page,
            self.profile_page,
            self.post_detail_page,
        ]
        for url in url_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location_authorized_user(self):
        """Проверка доступности URL-адреса авторизованым пользователям."""
        url_list = [
            START_PAGE,
            self.group_page,
            self.profile_page,
            self.post_detail_page,
            NEW_POST_PAGE,
            self.post_edit_page,
        ]
        for url in url_list:
            with self.subTest(url=url):
                response = self.authorized_client1.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404_url_exists_at_desired_location_anonymous(self):
        """Страница с ошибкой 404 (404/) доступна любому пользователю."""
        response = self.guest_client.get('/unknownpage/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.authorized_client1.get('/unknownpage/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_exists_at_desired_location_authorized_user(self):
        """Страница URL-адреса перенаправит анонимного пользователя."""
        url_list = [
            NEW_POST_PAGE,
            self.post_edit_page,
        ]
        for url in url_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_url_redirect_not_author_on_post_view(self):
        """Страница редактирования поста (posts/<post_id>/edit/)
        перенаправит не автора поста на страницу просмотра поста."""
        response = self.authorized_client2.get(self.post_edit_page)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.post_detail_page)

    def test_urls_uses_correct_template(self):
        """Проверка использования URL-адресом соответствующего HTML-шаблона."""
        url_templates_dict = {
            START_PAGE: 'posts/index.html',
            self.group_page: 'posts/group_list.html',
            self.profile_page: 'posts/profile.html',
            self.post_detail_page: 'posts/post_detail.html',
            NEW_POST_PAGE: 'posts/post_create.html',
            self.post_edit_page: 'posts/post_create.html',
        }
        for url, template in url_templates_dict.items():
            with self.subTest(url=url):
                response = self.authorized_client1.get(url)
                self.assertTemplateUsed(response, template)
