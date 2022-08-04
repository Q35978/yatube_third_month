from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_uses_correct_template_and_response(self):
        templates_url_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for addr, template in templates_url_names.items():
            with self.subTest(address=addr):
                response = self.guest_client.get(addr)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)
