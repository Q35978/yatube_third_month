# posts/tests/test_urls.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls.base import reverse
from http import HTTPStatus
from django.core.cache import cache
from ..models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
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
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Test post',
        )
        cls.templates_url_pub_pages = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': PostURLTests.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': PostURLTests.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': PostURLTests.post.id}):
                'posts/post_detail.html',
        }
        cls.templates_url_pr_pages = {
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': PostURLTests.post.id}):
                'posts/create_post.html',
        }
        cls.url_redirect_pr_pages = {
            reverse('posts:post_create'):
                reverse('users:login') + '?next='
                + reverse('posts:post_create'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostURLTests.post.pk},
            ):
                reverse('users:login') + '?next='
                + reverse('posts:post_edit', args=[PostURLTests.post.pk],),
        }
        cls.url_unexist_page = '/unexist_page/'

    def setUp(self):
        """Создаем дополнительный ряд клиентов (новый авторизированный и
        не авторизированный), так же задаем список урл и шаблонов
        для дальнейшей работы
        """
        self.guest_client = Client()
        self.authorised_client = Client()
        self.authorised_client.force_login(PostURLTests.user)
        cache.clear()

    def test_urls_uses_correct_template_public_pages(self):
        """Проверяем шаблоны создателем поста
        для публичных страниц
        """
        for addr, exp_templ in PostURLTests.templates_url_pub_pages.items():
            with self.subTest(address=addr):
                response = self.authorised_client.get(addr)
                self.assertTemplateUsed(response, exp_templ)

    def test_url_uses_correct_template_priv_pages(self):
        """Проверяем шаблоны создателем поста для
        страницы создания и редактирования поста
        """
        for addr, exp_templ in PostURLTests.templates_url_pr_pages.items():
            with self.subTest(address=addr):
                response = self.authorised_client.get(addr)
                self.assertTemplateUsed(response, exp_templ)

    def test_address_status_pub_pages_guest(self):
        """Проверяет доступность публичных страниц
        для гостя
        """
        for addr in PostURLTests.templates_url_pub_pages.keys():
            with self.subTest(address=addr):
                response = self.guest_client.get(addr)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def test_address_redirect_private_pages_guest(self):
        """Проверяет переадресацию cо страниц
        создания и редактирования для гостя
        """
        for addr, redir_page in PostURLTests.url_redirect_pr_pages.items():
            with self.subTest(address=addr):
                response = self.guest_client.get(addr)
                self.assertRedirects(
                    response,
                    redir_page
                )

    def test_address_status_pub_pages_guest(self):
        """Проверяет доступность несуществующей страницы поста
        для гостя
        """
        response = self.guest_client.get(PostURLTests.url_unexist_page)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )

    def test_address_status_pub_pages_authorised_client(self):
        """Проверяет доступность публичных страниц автором поста"""
        for addr in PostURLTests.templates_url_pub_pages.keys():
            with self.subTest(address=addr):
                response = self.authorised_client.get(addr)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def test_address_status_private_pages_authorised_client(self):
        """Проверяет доступность страниц редактирования
        и создания поста автором поста
        """
        for addr in PostURLTests.templates_url_pr_pages.keys():
            with self.subTest(address=addr):
                response = self.authorised_client.get(addr)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def test_address_status_pub_pages_authorised_client(self):
        """Проверяет доступность несуществующей страницы поста
        автором поста
        """
        response = self.authorised_client.get(PostURLTests.url_unexist_page)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )

    def test_address_status_private_pages_another_client(self):
        """Проверяет доступность страниц редактирования
        поста не автором поста
        """
        another_user = User.objects.create_user(username="AnotherRobot")
        another_client = Client()
        another_client.force_login(another_user)
        addr_edit_page = reverse(
            'posts:post_edit',
            kwargs={'post_id': PostURLTests.post.pk}
        )
        redir_page_edit = reverse(
            'posts:post_detail',
            kwargs={'post_id': PostURLTests.post.pk}
        )
        response = another_client.get(addr_edit_page)
        self.assertRedirects(
            response,
            redir_page_edit
        )

    def test_cache_work(self):
        """Проверяем что кеш хранит данные даже после удаления поста,
        пост не показвается после принудельной очистки кеша.
        """
        post = Post.objects.create(
            author=PostURLTests.user,
            text='RobotCacheText',
            group=PostURLTests.group,
        )
        addr = reverse('posts:index')
        response = self.guest_client.get(addr)
        self.assertContains(response, post)
        post.delete()
        response_2 = self.guest_client.get(addr)
        self.assertContains(response_2, post)
        cache.clear()
        response_3 = self.guest_client.get(addr)
        self.assertNotContains(response_3, post)
