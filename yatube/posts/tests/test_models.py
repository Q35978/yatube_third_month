from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post


User = get_user_model()


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовую модель"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='robot')
        cls.group = Group.objects.create(
            title='Testing group',
            slug='testing-slug',
            description='Testing description'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Test post',
        )

    def test_models_have_correct_object_name(self):
        """Проверяем функцию __str__"""
        model_str_dict = {
            PostModelTests.post:
                PostModelTests.post.text[:15],
            PostModelTests.group:
                PostModelTests.group.title,
        }
        for model, expected_str in model_str_dict.items():
            with self.subTest(model=model):
                self.assertEqual(
                    expected_str,
                    str(model)
                )

    def test_verbose_name(self):
        """Проверяем заголовки для пользователя"""
        post = PostModelTests.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_name in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_name
                )

    def test_help_text(self):
        """Проверяем текст-подсказку"""
        post = PostModelTests.post
        field_verboses = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_text in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_text
                )
