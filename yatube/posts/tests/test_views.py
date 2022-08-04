# posts/tests/test_views.py
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.cache import cache
from ..models import Post, Group, Comment, Follow
import shutil
import tempfile

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем пост для тестирования"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='Robot')
        cls.another_user = User.objects.create_user(username='AnotherRobot')
        cls.third_user = User.objects.create_user(username='ThirdRobot')
        cls.group = Group.objects.create(
            title='Testing group',
            slug='testing-slug',
            description='Testing description'
        )
        test_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        file_name = "test.gif"
        cls.uploaded = SimpleUploadedFile(
            name=file_name,
            content=test_gif,
            content_type="image/gif"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Test post',
            image=cls.uploaded,
        )
        cls.urls_page_obj_list = [
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': PostViewTests.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': PostViewTests.user.username}),
        ]
        cls.comment = Comment.objects.create(
            author=cls.user,
            text="RobotComment",
            post=cls.post,
        )

    @classmethod
    def tearDownClass(cls):
        """Удаляем тестовые медиа."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаем клиент зарегистрированного пользователя."""
        self.unauthorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTests.user)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(PostViewTests.another_user)
        self.third_authorized_client = Client()
        self.third_authorized_client.force_login(PostViewTests.third_user)
        cache.clear()

    def test_page_obj_page_show_correct_context(self):
        """Шаблон page_obj сформирован с правильным контекстом."""
        for addr in self.urls_page_obj_list:
            response = self.authorized_client.get(addr)
            testing_object = response.context['page_obj'][0]
            testing_obj_field_value = {
                testing_object.text: PostViewTests.post.text,
                testing_object.group: PostViewTests.group,
                testing_object.image: PostViewTests.post.image,
                testing_object.author: PostViewTests.user,
            }
            for page_field, obj_value in testing_obj_field_value.items():
                with self.subTest(field=page_field):
                    self.assertEqual(page_field, obj_value)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        addr = reverse('posts:post_detail',
                       kwargs={'post_id': PostViewTests.post.id})
        response = self.authorized_client.get(addr)
        testing_object = response.context['post']
        testing_comment = response.context["comments"][0]
        testing_obj_field_value = {
            testing_object.text: PostViewTests.post.text,
            testing_object.group: PostViewTests.group,
            testing_object.image: PostViewTests.post.image,
            testing_object.author: PostViewTests.user,
            testing_comment.text: PostViewTests.comment.text,
        }
        for obj_value, page_field in testing_obj_field_value.items():
            with self.subTest(field=page_field):
                self.assertEqual(page_field, obj_value)

    def test_post_not_in_any_group(self):
        """Проверка, что созданный пост не попал в группу,
        для которой не был предназначен.
        """
        wrong_group = Group.objects.create(
            title='Wrong testing group',
            slug='wrong-testing-slug',
            description='Wrong testing description'
        )
        addr = reverse('posts:group_list', args=[wrong_group.slug])
        response = self.authorized_client.get(addr)
        self.assertEqual(
            self.post not in response.context.get('page_obj').object_list,
            True
        )

    def test_post_on_right_group_page(self):
        """Проверка, что созданный пост попал в группу,
        для которой был предназначен.
        """
        addr = reverse('posts:group_list', args=[self.group.slug])
        response = self.authorized_client.get(addr)
        self.assertIn(
            self.post,
            response.context.get('page_obj').object_list
        )

    def test_post_on_main_page(self):
        """Проверка, что созданный пост попал
        на главную страницу.
        """
        addr = reverse('posts:index')
        response = self.authorized_client.get(addr)
        self.assertIn(
            self.post,
            response.context.get('page_obj').object_list
        )

    def test_new_post_page_show_correct_context(self):
        """Проверка, что страница создания поста показывает
        правильный контекст
        """
        addr = reverse('posts:post_create')
        response = self.authorized_client.get(addr)
        testing_field_value = {
            'text': None,
            'group': None,
        }
        for test_field, expect_value in testing_field_value.items():
            with self.subTest(field=test_field):
                testing_value = response.context['form'][test_field].value()
                self.assertEqual(testing_value, expect_value)

    def test_edit_post_page_show_correct_context(self):
        """Проверка, что страница редактирования поста показывает
        правильный контекст
        """
        addr = reverse('posts:post_edit',
                       kwargs={'post_id': PostViewTests.post.id})
        response = self.authorized_client.get(addr)
        testing_field_value = {
            'text': PostViewTests.post.text,
            'group': PostViewTests.group.id,
        }
        for test_field, expect_value in testing_field_value.items():
            with self.subTest(field=test_field):
                testing_value = response.context['form'][test_field].value()
                self.assertEqual(testing_value, expect_value)

    def test_paginator_correct_context(self):
        """Шаблон index, group_list и profile
        сформированы с корректным Paginator.
        """
        objects_for_paginator = []
        for i in range(0, 17):
            new_post = Post(
                author=PostViewTests.user,
                text='Testing post ' + str(i),
                group=PostViewTests.group
            )
            objects_for_paginator.append(new_post)
        Post.objects.bulk_create(objects_for_paginator)
        for addr in PostViewTests.urls_page_obj_list:
            with self.subTest(address=addr):
                response_page_1 = self.authorized_client.get(addr)
                response_page_2 = self.authorized_client.get(
                    addr + '?page=2'
                )
                self.assertEqual(
                    len(response_page_1.context.get('page_obj')),
                    10
                )
                self.assertEqual(
                    len(response_page_2.context.get('page_obj')),
                    8
                )

    def test_unable_create_comment_by_guest(self):
        """Проверяем что под гостем не создаются новые комментарии"""
        comments = Comment.objects.count()
        addr = reverse(
            'posts:add_comment',
            kwargs={
                'post_id': PostViewTests.post.id,
            }
        )
        text_for_comment = 'NewRobotComment'
        self.unauthorized_client.post(
            addr,
            data={'text': text_for_comment},
        )
        expected_comment = Comment.objects.filter(
            post=PostViewTests.post.id,
            text=text_for_comment
        )
        self.assertFalse(expected_comment)
        self.assertEqual(Comment.objects.count(), comments)

    def test_user_can_follow_another_user(self):
        """Авторизованный пользователь, может подписаться
        на другого пользователя.
        """
        response = self.another_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': PostViewTests.user.username}),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': PostViewTests.user.username})
        )
        follow_count = Follow.objects.count()
        self.assertEqual(follow_count, 1)

    def test_user_can_unfollows(self):
        """Авторизованный пользователь, может удалить из подписку
        на другого пользователя
        """
        response = self.another_authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': PostViewTests.user.username}),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': PostViewTests.user.username})
        )
        follow_count = Follow.objects.count()
        self.assertEqual(follow_count, 1)
        response = self.another_authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': PostViewTests.user.username}),
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': PostViewTests.user.username})
        )
        follow_count = Follow.objects.count()
        self.assertEqual(follow_count, 0)

    def test_new_post_user_appears_in_follow_index(self):
        """Новый пост пользователя отображается в ленте,
        в том случае, если пользователь подписан на автора.
        """
        test_text = 'test_text'
        test_post = Post.objects.create(
            author=self.user,
            text=test_text,
        )
        Follow.objects.create(
            user=self.another_user,
            author=self.user,
        )
        response = self.another_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(
            test_post,
            response.context.get('page_obj').object_list
        )

    def test_new_post_user_not_appear_in_follow_index_not_following(self):
        """Убедимся, новый пост пользователя,
        не отображается, кто на него не подписан.
        """
        test_text = 'test_text_unfollow'
        test_post = Post.objects.create(
            author=PostViewTests.user,
            text=test_text,
        )
        response = self.third_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(
            test_post,
            response.context.get('page_obj').object_list
        )
