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
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:login'))
        
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
        return HttpResponseRedirect(reverse('questionic:question', args=(question.id, )))    
    return render(request, 'questionic/post_question.html')

def question(request, question_id):
    if request.method == 'POST':
        user = User.objects.get(username=request.user.username)
        detail = request.POST['Detail']
        images = request.FILES.getlist('images')
        if  request.POST.get('comment'):
            from_question = Question.objects.get(id=request.POST['comment'])
            answerer = Account.objects.get(user=user)
            answer=Answer.objects.create(detail = detail, from_question=from_question, answerer=answerer)
            for image in images:
                AnswerFile.objects.create(answer=answer, image=image)
        else:
            from_answer = Answer.objects.get(id=request.POST['reply'])
            reply_answerer = Account.objects.get(user=user)
            reply_answer = ReplyAnswer.objects.create(detail = detail, from_answer=from_answer, reply_answerer=reply_answerer)
            for image in images:
                ReplyAnswerFile.objects.create(reply_answer=reply_answer, image=image)

    # Question
    question = Question.objects.get(id=question_id)
    list_images = QuestionFile.objects.filter(question=question)

    #Comment
    list_answer = Answer.objects.filter(from_question=question)

    dict_answer_image = {}
    dict_reply_image = {}
    for ans in list_answer:
        answerfile = AnswerFile.objects.filter(answer=ans)
        dict_answer_image.update({ans: answerfile})

        replyanswer = ReplyAnswer.objects.filter(from_answer=ans)
        dict_replyanswer = {}
        for reans in replyanswer:
            replyanswerfile = ReplyAnswerFile.objects.filter(reply_answer=reans)
            dict_replyanswer.update({reans: replyanswerfile})
        dict_reply_image.update({ans: dict_replyanswer})
 
    return render(request, 'questionic/question.html', {
        'question': question,
        'list_images': list_images,

        'dict_answer_image': dict_answer_image,
        'dict_reply_image': dict_reply_image
    })