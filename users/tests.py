from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from questionic.models import Account

# Create your tests here.

class UsersTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_superuser(username='admin', password='1234')
        Account.objects.create(user=user)

    def test_login_view_status_code(self):
        """ login view's status code is ok """

        c = Client()
        response = c.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_status_code(self):
        """ login view's status code is ok """

        c = Client()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('users:index'))
        self.assertEqual(response.status_code, 200)

    def test_can_not_login_status_code(self):
        """ login view's status code is ok """

        c = Client()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "123"})
        response = c.get(reverse('users:index'))
        self.assertEqual(response.status_code, 302)

    def test_logout_view_status_code(self):
        """ logout view's status code is ok """

        c = Client()
        response = c.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 200)
    
    def test_signup_status_code(self):
        """ signup view's status code is ok """

        c = Client()
        response = c.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)
    
    def test_register_signup_status_code(self):
        """ signup view's status code is ok """

        c = Client()
        response = c.post(reverse('users:signup'), {
            "username" : "test",
            "password": "1234",
            "email": "test@email.com",
            "firstname": "test",
            "lastname": "test"
        })
        response = c.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)