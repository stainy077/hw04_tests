from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post
from yatube.settings import (STATUS_CODE_404, STATUS_CODE_OK,
                             STATUS_CODE_REDIRECT)

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
            pub_date='2022-09-11',
            author=User.objects.create(username='NoName'),
            group=cls.group,
        )

    def setUp(self):
        """Создание клиентов."""
        self.guest_client = Client()

        user1 = get_user_model()
        self.user1 = user1.objects.get(username='NoName')
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)

        user2 = get_user_model()
        self.user2 = user2.objects.create(username='TestUser')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

        self.group_page = '/group/{0}/'.format(self.group.slug)
        self.profile_page = '/profile/{0}/'.format(self.post.author)
        self.post_detail_page = '/posts/{0}/'.format(self.post.id)
        self.post_edit_page = '/posts/{0}/edit/'.format(self.post.id)

    # Проверяем общедоступные страницы
    def test_index_url_exists_at_desired_location_anonymous(self):
        """Стартовая страница (/) доступна любому пользователю."""
        response = self.guest_client.get(START_PAGE)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
        response = self.authorized_client1.get(START_PAGE)
        self.assertEqual(response.status_code, STATUS_CODE_OK)

    def test_group_slug_url_exists_at_desired_location_anonymous(self):
        """Страница группы (group/test-slug/) доступна любому пользователю."""
        response = self.guest_client.get(self.group_page)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
        response = self.authorized_client1.get(self.group_page)
        self.assertEqual(response.status_code, STATUS_CODE_OK)

    def test_user_profile_url_exists_at_desired_location_anonymous(self):
        """Страница профиля (profile/<username>/)
        доступна любому пользователю."""
        response = self.guest_client.get(self.profile_page)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
        response = self.authorized_client1.get(self.profile_page)
        self.assertEqual(response.status_code, STATUS_CODE_OK)

    def test_post_view_url_exists_at_desired_location_anonymous(self):
        """Страница поста (posts/<post_id/) доступна любому пользователю."""
        response = self.guest_client.get(self.post_detail_page)
        self.assertEqual(response.status_code, STATUS_CODE_OK)
        response = self.authorized_client1.get(self.post_detail_page)
        self.assertEqual(response.status_code, STATUS_CODE_OK)

    def test_404_url_exists_at_desired_location_anonymous(self):
        """Страница с ошибкой 404 (404/) доступна любому пользователю."""
        response = self.guest_client.get('/unknownpage/')
        self.assertEqual(response.status_code, STATUS_CODE_404)
        response = self.authorized_client1.get('/unknownpage/')
        self.assertEqual(response.status_code, STATUS_CODE_404)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_url_new_exists_at_desired_location_logged_user(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client2.get(NEW_POST_PAGE)
        self.assertEqual(response.status_code, STATUS_CODE_OK)

    # Проверяем редиректы для неавторизованного пользователя
    def test_url_new_redirect_anonymous(self):
        """Страница создания нового поста (/create/) перенаправит
        анонимного пользователя."""
        response = self.guest_client.get(NEW_POST_PAGE)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)

    def test_post_edit_url_redirect_anonymous(self):
        """Страница редактирования поста (posts/<post_id>/edit/)
        перенаправит анонимного пользователя."""
        response = self.guest_client.get(self.post_edit_page)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)

    # Проверяем доступность для авторизованного пользователя, автора поста
    def test_post_edit_url_exists_at_desired_location_post_author(self):
        """Страница редактирования поста (posts/<post_id>/edit/)
        перенаправит не автора поста на страницу просмотра поста."""
        response = self.authorized_client1.get(self.post_edit_page)
        self.assertEqual(response.status_code, STATUS_CODE_OK)

    # Проверяем редирект для авторизованного пользователя, не автора поста
    def test_post_edit_url_redirect_not_author_on_post_view(self):
        """Страница редактирования поста (posts/<post_id>/edit/)
        перенаправит не автора поста на страницу просмотра поста."""
        response = self.authorized_client2.get(self.post_edit_page)
        self.assertEqual(response.status_code, STATUS_CODE_REDIRECT)
        self.assertRedirects(response, self.post_detail_page)

    # Проверка корректности вызываемых шаблонов для каждого адреса
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
