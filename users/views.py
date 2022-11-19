from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from questionic.models import Account, Notification, Question
from django.utils.timezone import datetime

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:login'))

    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    notification = Notification.objects.get(account=account)
    following = Account.objects.filter(follower=user.id).count()
    follower = Account.objects.filter(following=user.id).count()
    if Question.objects.filter(asker=account).count() == 0:
        post_history = []
    else:
        post_history = Question.objects.filter(asker=account).all().order_by("-date_asked")

    notification_alert = notification.alert_notification()
    return render(request, 'users/index.html', {
        'notification_alert': notification_alert,
        'account': account,
        'following' : following,
        'follower' : follower,
        'post_history' : post_history,
        'time_now': datetime.now(),
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('users:index'))
        else:
            return render(request, 'users/login.html', {
                'message': 'Invalid credentials.'
            })
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('questionic:index'))
    # return render(request, 'users/login.html', {
    #     'message': 'you are logged out.'
    # })

def signup(request):
    if request.method == "POST":
        umessage = ''
        pmessage = ''

        username = request.POST["username"]
        password = request.POST["password"]
        cpassword = request.POST["password confirmation"]
        email = request.POST["email"]
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]

        # check username
        if username == '' :
            umessage = 'please enter username.'
        else :
            account = User.objects.filter(username=username).count()
            if account != 0 :
                umessage = 'this username is already taken.'
        
        # check password
        if password == '' :
            pmessage = 'please enter password.'
        if password != cpassword :
            pmessage = 'confirm password is not same as password.'
        
        if umessage == '' and pmessage == '':
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            
            account = Account.objects.create(user=user)
            account.image_profile = '../static/assets/default_profile/profile-pic ('+ str(int(account.id) % 16)+').png'
            account.save()

            Notification.objects.create(account=account)

            return render(request, 'users/login.html')

        else:
            return render(request, 'users/signup.html', {
                'usermessage': umessage,
                'passwordmessage': pmessage,
                'username' : username,
                'password' : password,
                'cpassword' : cpassword,
                'email' : email,
                'first_name' : first_name,
                'last_name' : last_name,
            })
    return render(request, 'users/signup.html')

def userprofile(request, username):
    me = User.objects.get(username=request.user.username)
    myaccount = Account.objects.get(user=me)

    account = User.objects.filter(username=username).count()
    if account == 0 :
            return HttpResponse('User Not Found.', status = 400)

    if username == request.user.username:
        return HttpResponseRedirect(reverse('users:index'))

    user = User.objects.get(username=username)
    user_account = Account.objects.get(user=user)
    following = Account.objects.filter(follower=user.id).count()
    follower = Account.objects.filter(following=user.id).count()

    status = Account.objects.filter(user=request.user.id, following=user.id).count()
    if status == 0:
        follow_status = 'Follow'
    elif status == 1:
        follow_status = 'Unfollow'

    if Question.objects.filter(asker=user_account).count() == 0:
        post_history = []
    else:
        post_history = Question.objects.filter(asker=user_account).all().order_by("-date_asked")
    
    return render(request, 'users/userprofile.html', {
        "follow_status" : follow_status,
        "username" : username,
        "following" : following,
        "follower" : follower,
        "account": myaccount,
        'post_history' : post_history,
    })


def follow(request, status, userf):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:login'))
    
    user_f = User.objects.get(username=userf)
    userfollow = Account.objects.get(user=user_f.id)
    username = Account.objects.get(user=request.user.id)
    if status == 'Follow':
        username.following.add(userfollow)
    elif status == 'Unfollow':
        username.following.remove(userfollow)
    return HttpResponseRedirect(reverse('users:userprofile', args=(userf,)))

def editprofile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:login'))

    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    notification = Notification.objects.get(account=account)

    notification_alert = notification.alert_reply_notification()
    if request.method == "POST":
        if request.POST.get("password"):
            pmessage = ''

            password = request.POST["password"]
            if password == '' :
                pmessage = 'please enter password.'
            
            cpassword = request.POST["password confirmation"]
            if password != cpassword :
                pmessage = 'confirm password is not same as password.'
            
            if pmessage != '':
                return render(request, 'users/editprofile.html', {
                    'passwordmessage': pmessage,
                    'type': 'password'
                })
            user.set_password(password)
            user.save()
            print(password)
            print(user.password)

        elif request.POST.get("firstname"):
            image = request.FILES.getlist("image")

            user.first_name = request.POST["firstname"]
            user.last_name = request.POST["lastname"]
            user.email = request.POST["email"]
            user.save()
            for img in image:
                account.image_profile = img
            account.save()

        return HttpResponseRedirect(reverse('users:index'))   
    return render(request, 'users/editprofile.html', {
        "notification_alert": notification_alert,
        "account": account,
        'type': 'profile'
    })