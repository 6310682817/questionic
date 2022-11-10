from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from questionic.models import Account, Notification

def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:login'))

    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    notification = Notification.objects.get(account=account)

    notification_alert = notification.alert_reply_notification()
    return render(request, 'users/index.html', {
        'notification_alert': notification_alert
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
    return render(request, 'users/login.html', {
        'message': 'you are logged out.'
    })

def signup(request):
    if request.method == "POST":
        formu = User(request.POST)

        username = request.POST["username"]
        if username == '' :
            umessage = 'please enter username.'
        else :
            account = User.objects.filter(username=username).count()
            if account != 0 :
                umessage = 'this username is already taken.'
        

        password = request.POST["password"]
        if password == '' :
            pmessage = 'please enter password.'
        
        cpassword = request.POST["password confirmation"]
        if password != cpassword :
            pmessage = 'confirm password is not same as password.'
        
        if umessage != '' or pmessage != '':
            return render(request, 'users/signup.html', {
                'usermessage': umessage,
                'passwordmessage': pmessage
            })

        email = request.POST["email"]

        user = User.objects.create_user(username, email, password)
        user.first_name = request.POST["firstname"]
        user.last_name = request.POST["lastname"]
        user.save()

        account = Account.objects.create(user=user)
        Notification.objects.create(account=account)

        return render(request, 'users/login.html')

    return render(request, 'users/signup.html')

def userprofile(request, username):
    account = User.objects.filter(username=username).count()
    if account == 0 :
            return HttpResponse('User Not Found.', status = 400)

    user = User.objects.get(username=username)
    following = Account.objects.filter(follower=user.id).count()
    follower = Account.objects.filter(following=user.id).count()
    
    return render(request, 'users/userprofile.html', {
        "username" : username,
        "following" : following,
        "follower" : follower
    })


def follow(request, userf):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:login'))
    
    user_f = User.objects.get(username=userf)
    userfollow = Account.objects.get(user=user_f.id)
    
    username = Account.objects.get(user=request.user.id)
    username.following.add(userfollow)
    return HttpResponseRedirect(reverse('users:userprofile', args=(userf,)))