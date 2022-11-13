from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Account, Question, QuestionFile, Notification, Answer, AnswerFile, ReplyAnswer
from django.core.files.temp import NamedTemporaryFile

# Create your tests here.

class QuestionicTestCaseIteration1(TestCase):
    def setUp(self):
        user = User.objects.create_superuser(username='admin', password='1234')
        account = Account.objects.create(user=user, image_profile='./static/assets/default_profile/profile-pic (0).png')
        Notification.objects.create(account=account)


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

class QuestionicTestCaseIteration2(TestCase):
    def setUp(self):
        user1 = User.objects.create_superuser(username='admin', password='1234')
        account1 = Account.objects.create(user=user1, image_profile='./static/assets/default_profile/profile-pic (0).png')

        user2 = User.objects.create_superuser(username='user2', password='1234')
        account2 = Account.objects.create(user=user2, image_profile='./static/assets/default_profile/profile-pic (0).png')

        Notification.objects.create(account=account1)
        Notification.objects.create(account=account2)

    def test_not_login_question_status_code(self):
        """ question status code is OK """
        account = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account)
        account2 = Account.objects.last()
        answer = Answer.objects.create(detail="detail", from_question=question, answerer=account2)
        reply = ReplyAnswer.objects.create(detail="detail", from_answer=answer, reply_answerer=account)

        c = Client()
        response = c.get(reverse('questionic:question', args=(question.id,)))
        self.assertEqual(response.status_code, 200)

    def test_login_question_status_code(self):
        """ question status code is OK """
        account = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account)
        QuestionFile.objects.create(image="NamedTemporaryFile", question=question)

        c = Client()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('questionic:question', args=(question.id,)))
        self.assertEqual(response.status_code, 200)

    def test_answer_question_status_code(self):
        """ post_question status code is redirect """
        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)


        c = Client()
        image = NamedTemporaryFile()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.post(reverse('questionic:question', args=(question.id,)), {
            "Detail": "Detail",
            "comment": question.id,
            "images": image
        })
        self.assertEqual(response.status_code, 200)

    def test_reply_question_status_code(self):
        """ post_question status code is redirect """
        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)

        account2 = Account.objects.last()
        answer = Answer.objects.create(detail="detail", from_question=question, answerer=account2)
        c = Client()
        image = NamedTemporaryFile()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('questionic:question', args=(question.id,)))
        response = c.post(reverse('questionic:question', args=(question.id,)), {
            "Detail": "Detail",
            "reply": answer.id,
            "images": image
        })
        self.assertEqual(response.status_code, 200)

    def test_not_login_notification_status_code(self):
        """ notification status code is redirect """
    
        c = Client()
        response = c.get(reverse('questionic:notification'))
        self.assertEqual(response.status_code, 302)

    def test_login_notification_status_code(self):
        """ notification status code is redirect """
    
        c = Client()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('questionic:notification'))
        self.assertEqual(response.status_code, 200)
