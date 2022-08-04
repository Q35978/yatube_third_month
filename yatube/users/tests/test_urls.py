from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls.base import reverse
from http import HTTPStatus


User = get_user_model()


class UserURLTests(TestCase):
    def setUp(self):
        """Создаем клиентов и словари для тестирования"""
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Robot')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.templates_url_names = {
            reverse('users:login'): 'users/login.html',
            reverse('users:signup'): 'users/singup.html',
            reverse('users:password_change'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset_confirm',
                    kwargs={
                        'uidb64': 'NA', 'token': '5u2-61df9f91c57dffda7348'
                    }): 'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html'
        }
        self.templates_url_names_redirections = {
            reverse('users:password_reset'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
        }

    def test_urls_response_guest(self):
        """Проверяем статус страниц для гостя."""
        for addr in self.templates_url_names.keys():
            with self.subTest(address=addr):
                response = self.authorized_client.get(addr)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        for addr in self.templates_url_names_redirections.keys():
            with self.subTest(address=addr):
                response = self.guest_client.get(addr)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """Проверяем запрашиваемые шаблоны страниц через имена."""
        for addr, template in self.templates_url_names.items():
            with self.subTest(address=addr):
                response = self.authorized_client.get(addr)
                self.assertTemplateUsed(response, template)
        for addr, template in self.templates_url_names_redirections.items():
            with self.subTest(address=addr):
                response = self.authorized_client.get(addr)
                self.assertTemplateUsed(response, template)
