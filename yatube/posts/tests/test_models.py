from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        title = PostModelTest.group
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, str(title))

        text = PostModelTest.post
        expected_result = self.post.text[:15]
        self.assertEqual(expected_result, str(text))

    def test_models_have_correct_fields_names(self):
        """Проверяем корректность verbose_name."""
        fields_name_group = {
            'title': 'Название группы',
            'slug': 'Адрес группы',
            'description': 'Описание группы',
        }

        for field_name, name in fields_name_group.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    self.group._meta.get_field(field_name).verbose_name,
                    name)

        fields_name_post = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор'
        }

        for field_name, name in fields_name_post.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    self.post._meta.get_field(field_name).verbose_name,
                    name)
