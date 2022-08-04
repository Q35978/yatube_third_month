# posts/users/test_forms.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class UserFormTests(TestCase):
    def setUp(self):
        """Создаем клиент"""
        self.guest_client = Client()

    def test_create_user(self):
        """Создание нового прользователя."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Robot',
            'last_name': 'Cop',
            'username': 'RobotCop',
            'email': 'RobotCop@nypd.us',
            'password1': 'Q11223344Qe!',
            'password2': 'Q11223344Qe!'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        user = User.objects.last()
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(user.username, form_data['username'])
        self.assertEqual(user.first_name, form_data['first_name'])
        self.assertEqual(user.last_name, form_data['last_name'])
