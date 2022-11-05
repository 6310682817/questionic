from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:login'))
    return render(request, 'users/index.html')

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
        username = request.POST["username"]
        password = request.POST["password"]
        # cpassword = request.POST["password confirmation"]
        email = request.POST["email"]

        # if password != cpassword :
        #     form = NameForm(request.POST)
        #     return render({
        #         'message': 'Password incorrect.'
        #     })
        # else :
        user = User.objects.create_user(username, email, password)
        user.first_name = request.POST["firstname"]
        user.last_name = request.POST["lastname"]
        user.save()
        return render(request, 'users/login.html')

    return render(request, 'users/signup.html')