import shutil
import tempfile
from http.client import HTTPResponse

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test_User_1')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.post = Post.objects.create(
            author=self.user,
            text='test_post',
            image=self.uploaded
        )
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}):
                        'posts/group_list.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}):
                        'posts/post_detail.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}):
                        'posts/profile.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_form_context(self, response: HTTPResponse):
        """Поля формы соответствуют типам."""

        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.check_form_context(response)

    def test_post_edit_show_correct_context(self):
        """Шаблон страницы post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=(self.post.id,))
        )
        self.check_form_context(response)

    def test_cache_index(self):
        get_post = self.authorized_client.get(
            reverse('posts:index')).content
        Post.objects.create(
            author=self.user,
            text='Cache_post',
            image=self.uploaded
        )
        get_post_1 = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(get_post, get_post_1, 'Появился новый пост!')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test_User_2')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        posts = (Post(
            text=f'Тестовый текст {i}',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded) for i in range(13)
        )
        cls.post = Post.objects.bulk_create(posts)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def test_context_with_paginator(self):
        """Тестируем контекст с Paginator."""
        pages_names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user})
        )

        for page_name in pages_names:
            with self.subTest(page_name=page_name):
                response = self.authorized_client.get(page_name)
                self.assertEqual(len(response.context['page_obj']), 10)

        for page_name in pages_names:
            with self.subTest(page_name=page_name):
                response = self.authorized_client.get(
                    page_name, {'page': 2}
                )
                self.assertEqual(len(response.context['page_obj']), 3)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='author',
        )
        cls.follower = User.objects.create(
            username='follower',
        )
        cls.post = Post.objects.create(
            text='Test_follow',
            author=cls.author,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        self.count_follows = Follow.objects.count()
        cache.clear()

    def test_follow(self):
        """Подписка на автора."""
        self.author_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.follower}))
        self.assertEqual(Follow.objects.count(), self.count_follows + 1)
        self.assertTrue(
            Follow.objects.filter(
                author=self.follower,
                user=self.author,
            ).exists()
        )

    def test_unfollow(self):
        """Отписка от автора."""
        self.author_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.follower}))
        self.assertEqual(Follow.objects.count(), 0)
        self.assertFalse(
            Follow.objects.filter(
                author=self.follower,
                user=self.author,
            ).exists()
        )

    def test_follow_list_is_here(self):
        """Страница с пописками в контексте у пользователя."""
        Follow.objects.create(
            user=self.follower,
            author=self.author
        )
        response = self.follower_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(self.post, response.context['page_obj'].object_list)

    def test_notfollow_on_authors(self):
        """Страница стандартная у не подписавшихся."""
        response = self.author_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(self.post, response.context['page_obj'].object_list)

    def test_cant_follow_to_yourself(self):
        """Автор не может подписаться на себя."""
        self.author_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.follower}
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                author=self.author,
                user=self.author,
            ).exists()
        )
