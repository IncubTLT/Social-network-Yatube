import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем клиента и пост."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.author,
            group=self.group)
        self.posts_count = Post.objects.count()
        self.form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }

    def test_create_post(self):
        """Валидная форма создает запись."""
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.count(),
            self.posts_count + 1,
            'Пост не сохранен!'
        )
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    args=(self.author.username,))
        )
        self.assertTrue(
            Post.objects.filter(
                text=self.form_data['text'],
                group=self.form_data['group']
            ).exists()
        )

    def test_cant_create_existing_slug(self):
        """Проверка редактирования текста поста."""
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=self.form_data,
            follow=True
        )
        edited_post = Post.objects.get(id=self.post.id)
        self.assertEqual(
            edited_post.text,
            self.form_data['text'],
            'Текст поста не изменился.'
        )
        self.assertEqual(
            edited_post.group.id,
            self.form_data['group'],
            'slug изменился!'
        )
        # При изменении поста не создаётся новая запись.
        self.assertEqual(
            Post.objects.count(),
            self.posts_count,
            'Ошибочно создалась запись.'
        )
        # Страница отвечает.
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_image_in_(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'post_with_image',
            'group': self.group.id,
            'image': uploaded
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertTrue(Post.objects.filter(
            image='posts/small.gif'
        ).exists())

    def test_comment_add_authorized_user(self):
        """Авторизованный юзер добавляет коммент."""
        comments_count = Comment.objects.count()
        comment_text = {'text': 'Коммент'}
        self.authorized_client.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data=comment_text,
            follow=True
        )
        self.assertEqual(
            Comment.objects.count(),
            comments_count + 1,
            'Коммент не сохранен!'
        )
        # Убеждаемся что коммент появился в базе.
        self.assertTrue(
            Comment.objects.filter(text='Коммент')
        )

    def test_guest_user_cant_add_comment(self):
        """Невторизованный юзер не может добавить коммент."""
        guest_client = Client()
        comments_count = Comment.objects.count()
        comment_text = {'text': 'Коммент'}
        guest_client.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data=comment_text,
            follow=True
        )
        self.assertEqual(
            Comment.objects.count(),
            comments_count,
            'Коммент сохранен!'
        )
