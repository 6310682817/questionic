from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Account, Question, QuestionFile, Notification, Answer, AnswerFile, ReplyAnswer
from django.core.files.temp import NamedTemporaryFile
import json

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

    def test_answer_question_count(self):
        """ answer question follower count should be 1 """
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
        answer = Answer.objects.all()
        self.assertEqual(answer.count(), 1)

    def test_reply_answer_question_count(self):
        """ reply answer question follower count should be 1 """
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
        reply = ReplyAnswer.objects.all()
        self.assertEqual(reply.count(), 1)

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

class QuestionicTestCaseIteration3(TestCase):
    def setUp(self):
        user1 = User.objects.create_superuser(username='admin', password='1234')
        account1 = Account.objects.create(user=user1, image_profile='./static/assets/default_profile/profile-pic (0).png')

        user2 = User.objects.create_superuser(username='user2', password='1234')
        account2 = Account.objects.create(user=user2, image_profile='./static/assets/default_profile/profile-pic (0).png')

        Notification.objects.create(account=account1)
        Notification.objects.create(account=account2)

    def test_not_login_report_count(self):
        """ report count should be 0 """

        c = Client()
        account1 = Account.objects.first()

        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)
        question = Question.objects.first()
        response = c.get(reverse('questionic:report', args=("question", question.id,)))

        notification_account1 = Notification.objects.get(account=account1)
        self.assertEqual(notification_account1.qreport_notification.count(), 0)

    def test_question_report_admin_notification_count(self):
        """ question report count should be 1 """

        c = Client()
        account1 = Account.objects.first()

        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)
        question = Question.objects.first()
        response = c.post(reverse('users:login'), {"username" : "user2", "password": "1234"})
        response = c.get(reverse('questionic:report', args=("question", question.id,)))

        notification_account1 = Notification.objects.get(account=account1)
        self.assertEqual(notification_account1.qreport_notification.count(), 1)

    def test_answer_report_admin_notification_count(self):
        """ answer report count should be 1 """

        c = Client()
        account1 = Account.objects.first()

        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)
        answer = Answer.objects.create(detail="detail", from_question=question, answerer=account1)
        answer = Answer.objects.first()
        response = c.post(reverse('users:login'), {"username" : "user2", "password": "1234"})
        response = c.get(reverse('questionic:report', args=("answer", answer.id,)))

        notification_account1 = Notification.objects.get(account=account1)
        self.assertEqual(notification_account1.areport_notification.count(), 1)

    def test_reply_answer_report_admin_notification_count(self):
        """ reply answer report count should be 1 """

        c = Client()
        account1 = Account.objects.first()

        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)
        answer = Answer.objects.create(detail="detail", from_question=question, answerer=account1)
        reply_answer = ReplyAnswer.objects.create(detail="detail", from_answer=answer, reply_answerer=account1)
        reply_answer = ReplyAnswer.objects.first()

        response = c.post(reverse('users:login'), {"username" : "user2", "password": "1234"})
        response = c.get(reverse('questionic:report', args=("reply", reply_answer.id,)))

        notification_account1 = Notification.objects.get(account=account1)
        self.assertEqual(notification_account1.rreport_notification.count(), 1)

    def test_following_new_post_notification_count(self):
        """ follow notification count should be 1 """

        c = Client()
        account1 = Account.objects.first()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        c.get(reverse('users:follow', args=("Follow", "user2",)))

        c.post(reverse('users:login'), {"username" : "user2", "password": "1234"})
        image = NamedTemporaryFile()
        c.post(reverse('questionic:post_question'), {
            "Title": "title",
            "Detail": "detail",
            "Category": "category",
            "Grade": "grade",
            "images": image
        })
        
        notification_account1 = Notification.objects.get(account=account1)
        self.assertEqual(notification_account1.follow_notification.count(), 1)

    def test_index_not_login_status_code(self):
        """ index status code should be ok """

        c = Client()
        response = c.get(reverse('questionic:index'))
        self.assertEqual(response.status_code, 200)

    def test_index_login_status_code(self):
        """ index status code should be ok """

        c = Client()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('questionic:index'))
        self.assertEqual(response.status_code, 200)

    def test_fav_question_not_login_status_code(self):
        """ fav question status code should be 302 """

        c = Client()

        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)
        response = c.get(reverse('questionic:fav_question', args=(question.id, "fav")))
        self.assertEqual(response.status_code, 302)

    def test_fav_question_count(self):
        """ question faved count should be 1 """

        c = Client()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})

        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)
        response = c.get(reverse('questionic:fav_question', args=(question.id, "fav", )))
        self.assertEqual(question.fav_account.count(), 1)
    
    def test_unfav_question_count(self):
        """ question faved count should be 0 """

        c = Client()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})

        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)
        response = c.get(reverse('questionic:fav_question', args=(question.id, "fav", )))
        response = c.get(reverse('questionic:fav_question', args=(question.id, "unfav", )))
        self.assertEqual(question.fav_account.count(), 0)

    def test_search_answered_question(self):
        """ search result count code should be 1 """

        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)
        answer = Answer.objects.create(detail="detail", from_question=question, answerer=account1)

        c = Client()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.post(reverse('questionic:question', args=(question.id,)), data={
            "Detail": "detail",
            "comment": question.id
        })
        response = c.get(reverse('questionic:search'), data={
            "search_keyword": "title",
            "category": "category",
            "grade": "grade",
            "status": "answer"
        })
        self.assertEqual(response.context['question_search'].count(),1)

    def test_search_unanswered_question(self):
        """ search result count code should be 1 """

        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)

        c = Client()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        
        response = c.get(reverse('questionic:search'), data={
            "search_keyword": "title",
            "category": "category",
            "grade": "grade",
            "status": "unanswer"
        })
        self.assertEqual(response.context['question_search'].count(),1)
    
    def test_search_answered_question_not_login(self):
        """ search result count code should be 1 """

        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)
        answer = Answer.objects.create(detail="detail", from_question=question, answerer=account1)

        c = Client()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.post(reverse('questionic:question', args=(question.id,)), data={
            "Detail": "detail",
            "comment": question.id
        })
        response = c.get(reverse('users:logout'))
        response = c.get(reverse('questionic:search'), data={
            "search_keyword": "title",
            "category": "category",
            "grade": "grade",
            "status": "answer"
        })
        self.assertEqual(response.context['question_search'].count(),1)

    def test_search_unanswered_question_not_login(self):
        """ search result count code should be 1 """

        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)

        c = Client()
        response = c.get(reverse('questionic:search'), data={
            "search_keyword": "title",
            "category": "category",
            "grade": "grade",
            "status": "unanswer"
        })
        self.assertEqual(response.context['question_search'].count(),1)

    def test_delete_not_login_status_code(self):
        """ delete status code should be 302 """

        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)

        c = Client()

        response = c.get(reverse('questionic:delete', args=('question', question.id, )))
        self.assertEqual(response.status_code, 302)

    def test_delete_question(self):
        """ question count should be 1 """

        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)

        c = Client()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('questionic:delete', args=('question', question.id, )))
        self.assertEqual(Question.objects.all().count(), 0)

    def test_delete_answer(self):
        """ answer count should be 1 """

        account = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account)
        answer = Answer.objects.create(detail="detail", answerer=account, from_question=question)

        c = Client()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('questionic:delete', args=('answer', answer.id, )))
        self.assertEqual(Answer.objects.all().count(), 0)
    
    def test_delete_reply_answer(self):
        """ reply count should be 1 """

        account = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account)
        answer = Answer.objects.create(detail="detail", answerer=account, from_question=question)
        reply_answer = ReplyAnswer.objects.create(detail="detail", reply_answerer=account, from_answer=answer)

        c = Client()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('questionic:delete', args=('reply', reply_answer.id, )))
        self.assertEqual(ReplyAnswer.objects.all().count(), 0)

    def test_delete_invalid_user_status_code(self):
        """ status code should be 302 """

        user3 = User.objects.create_user(username='user3', password='1234')
        account3 = Account.objects.create(user=user3, image_profile='./static/assets/default_profile/profile-pic (0).png')

        account = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account)
        answer = Answer.objects.create(detail="detail", answerer=account, from_question=question)
        reply_answer = ReplyAnswer.objects.create(detail="detail", reply_answerer=account, from_answer=answer)

        c = Client()
        c.post(reverse('users:login'), {"username" : "user3", "password": "1234"})

        response = c.get(reverse('questionic:delete', args=('question', question.id, )))
        self.assertEqual(response.status_code, 302)

        response = c.get(reverse('questionic:delete', args=('answer', answer.id, )))
        self.assertEqual(response.status_code, 302)

        response = c.get(reverse('questionic:delete', args=('reply', reply_answer.id, )))
        self.assertEqual(response.status_code, 302)
    
    def test_not_login_notification_alert(self):
        """ notification alert should be 0 """

        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)

        c = Client()
        response = c.get(reverse('questionic:notification_alert'))

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'notification_alert': 0}
        )
    
    def test_login_notification_alert(self):
        """ notification alert should be 0 """

        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)

        c = Client()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('questionic:notification_alert'))

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'notification_alert': 0}
        )
    
    def test_notification_not_staff(self):
        """ notification response context should be 6 """

        user3 = User.objects.create_user(username='user3', password='1234')
        account3 = Account.objects.create(user=user3, image_profile='./static/assets/default_profile/profile-pic (0).png')
        notification3 =  Notification.objects.create(account=account3)
        
        c = Client()
        c.post(reverse('users:login'), {"username" : "user3", "password": "1234"})
        response = c.get(reverse('questionic:notification'))
        self.assertEqual(response.context.get('rreport_notifications'), None)

    def test_reply_notification_form_other_user(self):

        account1 = Account.objects.first()
        notification1 =  Notification.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)
        
        user3 = User.objects.create_user(username='user3', password='1234')
        account3 = Account.objects.create(user=user3, image_profile='./static/assets/default_profile/profile-pic (0).png')
        notification3 =  Notification.objects.create(account=account3)
        
        c = Client()
        c.post(reverse('users:login'), {"username" : "user3", "password": "1234"})
        image = NamedTemporaryFile()
        response = c.post(reverse('questionic:question', args=(question.id,)), {
            "Detail": "Detail",
            "comment": question.id,
            "images": image
        })
        self.assertEqual(Notification.objects.filter(account=account1).count(), 1)

class QuestionicTestCaseOther(TestCase):
    def setUp(self):
        user1 = User.objects.create_superuser(username='admin', password='1234')
        account1 = Account.objects.create(user=user1, image_profile='./static/assets/default_profile/profile-pic (0).png')

        user2 = User.objects.create_superuser(username='user2', password='1234')
        account2 = Account.objects.create(user=user2, image_profile='./static/assets/default_profile/profile-pic (0).png')

        Notification.objects.create(account=account1)
        Notification.objects.create(account=account2)
    
    def test_not_login_about_status_code(self):
        """ status code should be 200 """

        c = Client()
        response = c.get(reverse('questionic:about'))
        self.assertEqual(response.status_code, 200)

    def test_login_about_status_code(self):
        """ status code should be 200 """

        c = Client()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('questionic:about'))
        self.assertEqual(response.status_code, 200)


