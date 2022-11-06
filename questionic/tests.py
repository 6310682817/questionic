from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Account, Question, QuestionFile
from django.core.files.temp import NamedTemporaryFile

# Create your tests here.

class QuestionicTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_superuser(username='admin', password='1234')
        Account.objects.create(user=user)

    def test_post_question_status_code(self):
        """ post_question status code is ok """

        c = Client()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('questionic:post_question'))
        self.assertEqual(response.status_code, 200)

    def test_not_login_post_question_status_code(self):
        """ post_question status code is redirect """

        c = Client()
        response = c.get(reverse('questionic:post_question'))
        self.assertEqual(response.status_code, 302)

    def test_create_question_post_question(self):
        """ Question object should has 1 object"""

        c = Client()
        image = NamedTemporaryFile()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        c.post(reverse('questionic:post_question'), {
            "Title": "title",
            "Detail": "detail",
            "Category": "category",
            "Grade": "grade",
            "images": image
        })
        self.assertEqual(Question.objects.all().count(), 1)
