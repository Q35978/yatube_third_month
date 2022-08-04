# posts/posts/test_forms.py
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls.base import reverse
from django.core.cache import cache
from ..models import Post, Group
import shutil
import tempfile
from django.conf import settings

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем пост для тестирования"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='Robot')
        cls.group = Group.objects.create(
            title='Testing group',
            slug='testing-slug',
            description='Testing description'
        )
        cls.post_with_group = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Test post',
        )
        cls.post_without_group = Post.objects.create(
            author=cls.user,
            text='Test post',
        )
        cls.url_create = reverse('posts:post_create')
        cls.url_create_redirect = reverse(
            "posts:profile",
            kwargs={"username": PostFormTests.user.username},
        )
        cls.url_edit = reverse(
            "posts:post_edit",
            kwargs={"post_id": PostFormTests.post_with_group.id},
        )
        cls.url_edit_redirect = reverse(
            "posts:post_detail",
            kwargs={"post_id": PostFormTests.post_with_group.id},
        )

    @classmethod
    def tearDownClass(cls):
        """Удаляем тестовые медиа."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем авторизированный клиент"""
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)
        cache.clear()

    def test_create_post_with_group(self):
        """Валидная форма создает запись в Post с указанием группы"""
        posts_count = Post.objects.count()
        test_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        file_name = "test.gif"
        uploaded = SimpleUploadedFile(
            name=file_name,
            content=test_gif,
            content_type="image/gif",
        )
        form_data = {
            "text": PostFormTests.post_with_group.text,
            "group": PostFormTests.group.id,
            "image": uploaded,
        }
        response = self.authorized_client.post(
            PostFormTests.url_create,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            PostFormTests.url_create_redirect,
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest("id")
        self.assertEqual(post.text, PostFormTests.post_with_group.text)
        self.assertEqual(post.group, PostFormTests.post_with_group.group)
        self.assertEqual(post.image, f'posts/{file_name}')

    def test_create_post_without_group(self):
        """Валидная форма создает запись в Post без указания группы"""
        posts_count = Post.objects.count()
        form_data = {
            "text": PostFormTests.post_without_group.text,
        }
        response = self.authorized_client.post(
            PostFormTests.url_create,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            PostFormTests.url_create_redirect,
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest("id")
        self.assertEqual(post.text, PostFormTests.post_without_group.text)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""

        form_data = {"text": "Edited text"}
        response = self.authorized_client.post(
            PostFormTests.url_edit,
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            PostFormTests.url_edit_redirect,
        )
        edit_post = Post.objects.get(id=PostFormTests.post_with_group.id)
        self.assertEqual(edit_post.text, form_data["text"])
