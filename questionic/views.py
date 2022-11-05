from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Question, Account, QuestionFile, Answer, AnswerFile, ReplyAnswer, ReplyAnswerFile
from django.contrib.auth.models import User

# Create your views here.

def index(request):
    return render(request, 'questionic/index.html')

def about(request):
    return render(request, 'questionic/about.html')

def post_question(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.user.username)

        # tags = request.POST['Tags']
        title = request.POST['Title']
        detail = request.POST['Detail']
        category = request.POST['Category']
        grade = request.POST['Grade']
        asker = Account.objects.get(user=user)
        images = request.FILES.getlist('images')

        question=Question.objects.create(title = title, detail = detail,  category=category, grade=grade, asker=asker)

        for img in images:
            QuestionFile.objects.create(question=question, image=img)
        # return HttpResponseRedirect(reverse('questionic:question', args=(question.id, )))    
    return render(request, 'questionic/post_question.html')