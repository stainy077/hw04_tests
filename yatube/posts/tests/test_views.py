# import shutil

# import tempfile

# import time

from django import forms

# from django.conf import settings

from django.contrib.auth import get_user_model

# from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import Client, TestCase

from django.urls import reverse

from posts.models import Group, Post
# from posts.views import post_create

# from yatube.settings import POSTS_COUNT  # MEDIA_ROOT,

# # @override_settings(MEDIA_ROOT='temp_media')


class PostPagesTest(TestCase):
    """Создание экземпляров моделей Post и Group."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
#         settings.MEDIA_ROOT = tempfile.mkdtemp(
#             prefix='pages_',
#             dir=settings.BASE_DIR,
#         )

        User = get_user_model()
        cls.test_user = User.objects.create(username='NoName')
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
            pub_date='2022-09-12',
            author=cls.test_user,
            group=cls.ok_group,
        )

#     @classmethod
#     def tearDownClass(cls):
#         shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
#         super().tearDownClass()

    def setUp(self):
        """ Создание неавторизованного клиента и
        клиента с авторизованным пользователем."""
        self.guest_client = Client()

        user1 = get_user_model()
        self.user1 = user1.objects.get(username='NoName')
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)

        user2 = get_user_model()
        self.user2 = user2.objects.create(username='TestUser')
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

    # Проверка передачи в шаблоны корректного контекста
    # def test_index_page_show_correct_context(self):
    #     """View-функция страницы index передает правильный контекст."""
    #     response = self.authorized_client1.get(reverse('posts:index'))
    #     # form_fields = {}
    #     # test_post_text = response.context.get('page')[0].text
    #     # test_post_author = response.context.get('page')[0].author.username
    #     # test_post_group = response.context.get('page')[0].group.title

    #     # self.assertEqual(test_post_text, 'Тестовое сообщение!!!')
    #     # self.assertEqual(test_post_author, 'NoName')
    #     # self.assertEqual(test_post_group, 'Правильная тестовая группа')

    #     post = response.context['page_obj'][0]
    #     self.checking_context(post)
#         context_page = response.context.get('page_obj')
#         for post in context_page:
#             self.assertIsInstance(post, Post)
#             self.assertEqual(post.author, self.post.author)
#             self.assertEqual(post.group, self.post.group)
# ​

#     def test_group_page_show_correct_context(self):
#         """View-функция страницы group передает правильный контекст."""
#         response = self.authorized_client_1.get(
#             reverse('group_list', kwargs={'slug': self.ok_group.slug})
#         )

#         test_group_title = response.context.get('group').title
#         test_group_slug = response.context.get('group').slug
#         test_group_description = response.context.get('group').description

#         self.assertEqual(test_group_title, 'Правильная тестовая группа')
#         self.assertEqual(test_group_slug, 'ok-slug')
#         self.assertEqual(test_group_description, 'Описание правильной группы')

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

#     def test_profile_page_show_correct_context(self):
#         """View-функция страницы профайла передает правильный контекст."""
#         response = self.authorized_client_2.get(reverse('profile', kwargs={
#             'username': self.test_post.author
#         }))

#         test_profile_posts = response.context.get('page')[0].text
#         test_profile_group = response.context.get('page')[0].group.title

#         self.assertEqual(test_profile_posts, 'Тестовое сообщение!!!')
#         self.assertEqual(test_profile_group, 'Правильная тестовая группа')

#     def test_post_view_show_correct_context(self):
#         """View-функция страницы поста передает правильный контекст."""
#         response = self.authorized_client_2.get(reverse('post_view', kwargs={
#             'username': self.test_post.author,
#             'post_id': self.test_post.id
#         }))

#         post_view_text = response.context.get('post').text
#         post_view_group = response.context.get('post').group.title
#         self.assertEqual(post_view_text, 'Тестовое сообщение!!!')
#         self.assertEqual(post_view_group, 'Правильная тестовая группа')

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

    # def test_post_detail_page_show_correct_context(self):
    #     """View-функция страницы просмотра поста передает правильный контекст."""
    #     response = self.authorized_client1.get(
    #         reverse(
    #             'posts:post_detail',
    #             kwargs={'post_id': self.test_post.id},
    #         ),
    #     )
    #     form_fields = {
    #         'text': forms.fields.CharField,
    #         'group': forms.fields.ChoiceField,
    #     }

    #     for field_name, field_format in form_fields.items():
    #         with self.subTest(value=field_name):
    #             form_field = (
    #                 response.context.get('form').fields.get(field_name)
    #             )
    #             self.assertIsInstance(form_field, field_format)

    # def test_post_in_right_group(self):
    #     """Пост попал в нужную группу"""
    #     groups_list = {
    #         'ok_group': reverse(
    #             'posts:group_list',
    #             kwargs={'slug': self.ok_group.slug},
    #         ),
    #         'wrong_group': reverse(
    #             'posts:group_list',
    #             kwargs={'slug': self.wrong_group.slug}
    #         )
    #     }
    #     for some_group, reverse_name in groups_list.items():
    #         with self.subTest():
    #             response = self.authorized_client1.get(reverse_name)
    #             posts_in_group = response.context.get('page')
                # if some_group == 'ok_group':
                #     self.assertIn(self.test_post, posts_in_group)
    #             else:
    #                 self.assertNotIn(self.test_post, posts_in_group)

    # def test_main_page_display_post(self):
    #     """Пост видно на главной странице"""
    #     response = self.authorized_client1.get(reverse('posts:index'))
    #     main_page_view = response.context.get('page')
    #     self.assertIn(self.test_post, main_page_view)

#     def test_indext_page_list_is_1(self):
#         """На стартовую страницу передаётся ожидаемое количество постов"""
#         response = self.authorized_client_1.get(reverse('index'))
#         self.assertTrue(len(response.context['page']) <= POSTS_COUNT)

#         response_1 = self.authorized_client_1.get(reverse('index'))
#         response_2 = self.authorized_client_1.get(reverse('group', kwargs={
#             'slug': tim_group.slug,
#         }))
#         response_3 = self.authorized_client_1.get(reverse('profile', kwargs={
#             'username': tim_post.author,
#         }))
#         response_4 = self.authorized_client_1.get(reverse('post_view', kwargs={
#             'username': tim_post.author,
#             'post_id': tim_post.id,
#         }))

#         test_index_image = response_1.context.get('page')[0].image
#         test_group_image = response_2.context.get('page')[0].image
#         test_profile_image = response_3.context.get('page')[0].image
#         test_post_view_image = response_4.context.get('post').image

#         self.assertEqual(test_index_image, tim_post.image)
#         self.assertEqual(test_group_image, tim_post.image)
#         self.assertEqual(test_profile_image, tim_post.image)
#         self.assertEqual(test_post_view_image, tim_post.image)
