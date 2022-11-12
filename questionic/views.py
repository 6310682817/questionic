from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Question, Account, QuestionFile, Answer, AnswerFile
from .models import ReplyAnswer, ReplyAnswerFile, Notification
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse

# Create your views here.

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'questionic/index.html')

    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    notification = Notification.objects.get(account=account)

    notification_alert = notification.alert_reply_notification()
    return render(request, 'questionic/index.html', {
        "notification_alert": notification_alert,
        "account": account
    })

def about(request):
    if not request.user.is_authenticated:
        return render(request, 'questionic/about.html')
    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    notification = Notification.objects.get(account=account)

    notification_alert = notification.alert_reply_notification()
    return render(request, 'questionic/about.html', {
        "notification_alert": notification_alert,
        "account": account
    })

def post_question(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:login'))
    
    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    notification = Notification.objects.get(account=account)

    if request.method == 'POST':

        # tags = request.POST['Tags']
        title = request.POST['Title']
        detail = request.POST['Detail']
        category = request.POST['Category']
        grade = request.POST['Grade']
        asker = Account.objects.get(user=user)
        images = request.FILES.getlist('images')

        question = Question.objects.create(title=title, detail=detail,  category=category, grade=grade, asker=asker)

        for img in images:
            QuestionFile.objects.create(question=question, image=img)
        return HttpResponseRedirect(reverse('questionic:question', args=(question.id, )))  
        
    notification_alert = notification.alert_reply_notification()  
    return render(request, 'questionic/post_question.html', {
        "notification_alert": notification_alert,
        "account": account
    })

def question(request, question_id):
   
    if not request.user.is_authenticated:
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
        'dict_reply_image': dict_reply_image,
    })

    user = User.objects.get(username=request.user.username)
    myaccount = Account.objects.get(user=user)
    account = Account.objects.get(user=user)
    notification = Notification.objects.get(account=myaccount)
    notification_alert = notification.alert_reply_notification()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('users:login'))

        detail = request.POST['Detail']
        images = request.FILES.getlist('images')
        if  request.POST.get('comment'):
            from_question = Question.objects.get(id=request.POST['comment'])
            answerer = Account.objects.get(user=user)
            answer=Answer.objects.create(detail = detail, from_question=from_question, answerer=answerer)
            for image in images:
                AnswerFile.objects.create(answer=answer, image=image)
            
            if not from_question.asker == answerer:
                Notification.objects.get(account=from_question.asker).reply_notification.add(answer)
                
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
        'myaccount': myaccount,
        'dict_answer_image': dict_answer_image,
        'dict_reply_image': dict_reply_image,
        'notification_alert': notification_alert,
        "account": account
    })

def notification(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:login'))

    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    notification = Notification.objects.get(account=account)

    notification.reply_notification_count = notification.reply_notification.count()
    notification.save()
    notification_alert = notification.alert_reply_notification()
    notifications = notification.reply_notification.all().order_by('-date_answered')
    return render(request, 'questionic/notification.html', {
        "notification_alert": notification_alert,
        "notifications": notifications,
        "account": account
    })

def search(request):
    if not request.user.is_authenticated:
        return render(request, 'questionic/search.html', {
        })

    
    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    notification = Notification.objects.get(account=account)
    notification_alert = notification.alert_reply_notification()

    search_keyword = ""
    if request.method == "GET":
        search_keyword = request.GET['search_keyword']
        question_search = Question.objects.filter(Q(title__contains=search_keyword) | Q(detail__contains=search_keyword))
    return render(request, 'questionic/search.html', {
        "notification_alert": notification_alert,
        "search_keyword": search_keyword,
        "question_search": question_search,
        "account": account
    })

def notification_alert(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        account = Account.objects.get(user=user)
        notification = Notification.objects.get(account=account)
        notification_alert = notification.alert_reply_notification()
        return JsonResponse({
            'notification_alert':notification_alert,
        })
    return JsonResponse({
            'notification_alert':0,
    })

