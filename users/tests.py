from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from questionic.models import Account, Notification, Question
from django.core.files.temp import NamedTemporaryFile

# Create your tests here.

class UsersTestCaseIteration1(TestCase):
    def setUp(self):
        user = User.objects.create_superuser(username='admin', password='1234')
        account = Account.objects.create(user=user, image_profile='../static/assets/default_profile/profile-pic (0).png')
        Notification.objects.create(account=account)


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
        self.assertEqual(response.status_code, 302)
    
    def test_signup_status_code(self):
        """ signup view's status code is ok """

        c = Client()
        response = c.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)
    
    def test_valid_register_signup_status_code(self):
        """ signup view's status code is ok """

        c = Client()
        response = c.post(reverse('users:signup'), {
            "username" : "test",
            "password": "1234",
            "password confirmation": "1234",
            "email": "test@email.com",
            "firstname": "test",
            "lastname": "test"
        })
        response = c.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)

    def test_invalid_register_signup_status_code(self):
        """ signup view's status code is ok """

        c = Client()
        response = c.post(reverse('users:signup'), {
            "username" : "",
            "password": "",
            "password confirmation": "",
            "email": "",
            "firstname": "",
            "lastname": ""
        })
        self.assertEqual(response.status_code, 200)

class UsersTestCaseIteration2(TestCase):
    def setUp(self):
        user1 = User.objects.create_superuser(username='admin', password='1234')
        account1 = Account.objects.create(user=user1, image_profile='./static/assets/default_profile/profile-pic (0).png')

        user2 = User.objects.create(username='user2', password='1234')
        account2 = Account.objects.create(user=user2, image_profile='./static/assets/default_profile/profile-pic (0).png')

        Notification.objects.create(account=account1)
        Notification.objects.create(account=account2)

    
    def test_userporfile_status_code(self):
        """ userporfile view's status code is ok """

        c = Client()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('users:userprofile', args=("user2",)))
        self.assertEqual(response.status_code, 200)

    def test_not_found_userporfile_status_code(self):
        """ userporfile view's status code is 400 """

        c = Client()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('users:userprofile', args=("user1",)))
        self.assertEqual(response.status_code, 400)

    def test_not_login_follow_user_count(self):
        """ follow view's status code is 302 """

        c = Client()
        response = c.get(reverse('users:follow', args=("Follow", "user2",)))
        account2 = Account.objects.last()
        self.assertEqual(account2.follower.count(), 0)

    def test_login_follow_user_count(self):
        """ account follower count should be 1 """

        c = Client()
        account2 = Account.objects.last()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('users:follow', args=("Follow", "user2",)))
        self.assertEqual(account2.follower.count(), 1)

class UsersTestCaseIteration3(TestCase):
    def setUp(self):
        user1 = User.objects.create_superuser(username='admin', password='1234')
        account1 = Account.objects.create(user=user1, image_profile='./static/assets/default_profile/profile-pic (0).png')

        user2 = User.objects.create(username='user2', password='1234')
        account2 = Account.objects.create(user=user2, image_profile='./static/assets/default_profile/profile-pic (0).png')

        Notification.objects.create(account=account1)
        Notification.objects.create(account=account2)

    def test_follow_unfollow_button_status_code(self):
        """ userprofile view's status code is 200 """

        c = Client()
        account2 = Account.objects.last()
        c.get(reverse('users:userprofile', args=("user2",)))

        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        c.get(reverse('users:userprofile', args=("user2",)))

        c.get(reverse('users:follow', args=("Follow", "user2",)))
        response = c.get(reverse('users:userprofile', args=("user2",)))
        self.assertEqual(response.status_code, 200)

    def test_login_unfollow_user_count(self):
        """ account follower count should be 0 """

        c = Client()
        account2 = Account.objects.last()
        c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        c.get(reverse('users:follow', args=("Follow", "user2",)))
        c.get(reverse('users:follow', args=("Unfollow", "user2",)))
        self.assertEqual(account2.follower.count(), 0)

    def test_not_login_edit_profile_status_code(self):
        """ not login edit profile's status code is 302 """

        c = Client()
        response = c.get(reverse('users:editprofile'))
        self.assertEqual(response.status_code, 302)

    def test_login_edit_profile_status_code(self):
        """ login edit profile's status code is 200 """

        c = Client()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('users:editprofile'))
        self.assertEqual(response.status_code, 200)

    def test_edit_profile_status_code(self):
        """ edit profile's status code is 302 """

        c = Client()
        image = NamedTemporaryFile()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.post(reverse('users:editprofile'), {"firstname" : "test", 
                                            "lastname ": "test", 
                                            "email": "test@test.com",
                                            "image": image,
                                            "Save Profile": "Save Profile"})
        self.assertEqual(response.status_code, 302)

    def test_edit_password_empty_status_code(self):
        """ edit profile empty's status code is 200 """
        
        c = Client()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.post(reverse('users:editprofile'), {"password": '',
                                            "password confirmation ": '',
                                            "Save Password": "Save Password"})
        self.assertEqual(response.status_code, 200)
    
    def test_edit_password_not_same_status_code(self):
        """ edit profile not same's status code is 200 """

        c = Client()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.post(reverse('users:editprofile'), {"password" : "test", 
                                            "password confirmation ": "test123",
                                            "Save Password": "Save Password"})
        self.assertEqual(response.status_code, 200)

    def test_edit_password_valid_status_code(self):
        """ edit profile valid's status code is 302 """

        c = Client()
        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.post(reverse('users:editprofile'), {"password" : "test", 
                                            "password confirmation ": "test",
                                            "Save Password": "Save Password"})
        self.assertEqual(response.status_code, 302)

    def test_signup_username_is_already_taken_status_code(self):
        """ signup view's status code is ok """

        c = Client()
        response = c.post(reverse('users:signup'), {
            "username" : "user2",
            "password": "1234",
            "password confirmation": "12",
            "email": "",
            "firstname": "",
            "lastname": ""
        })
        self.assertEqual(response.status_code, 200)

    def test_user_profile_status_code(self):
        """ user profile view's status code is ok """
        """ reponse context post_history count is 1 """

        c = Client()
        account1 = Account.objects.first()
        question = Question.objects.create(title="title", detail="detail", category="category", grade="grade", asker=account1)

        response = c.post(reverse('users:login'), {"username" : "admin", "password": "1234"})
        response = c.get(reverse('users:userprofile', args=("admin",)))
        response = c.get(reverse('users:index'))
        self.assertEqual(response.status_code, 200)

        response = c.get(reverse('users:logout'))
        response = c.post(reverse('users:login'), {"username" : "user2", "password": "1234"})
        response = c.get(reverse('users:userprofile', args=(account1.user.username,)))
        self.assertEqual(response.context['post_history'].count(), 1)
