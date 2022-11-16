from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Question, Account, QuestionFile, Answer, AnswerFile
from .models import ReplyAnswer, ReplyAnswerFile, Notification
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.utils.timezone import datetime

# Create your views here.

def index(request):
    if not request.user.is_authenticated:
        question_lastest = Question.objects.all().order_by("-date_asked")[:10]
        question_popular = Question.objects.all().order_by('-faved')[:10]

        print(question_popular)
        return render(request, 'questionic/index.html', {
            "question_lastest": question_lastest,
            "question_popular": question_popular,
            "time_now": datetime.now(),
        })

    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    notification = Notification.objects.get(account=account)
    notification_alert = notification.alert_reply_notification()

    question_lastest = Question.objects.all().order_by("-date_asked")[:10]
    question_popular = Question.objects.all().order_by('-faved')[:10]

    return render(request, 'questionic/index.html', {
        "notification_alert": notification_alert,
        "account": account,
        "question_lastest": question_lastest,
        "question_popular": question_popular,
        "time_now": datetime.now(),
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

        if  request.POST.get('comment'):
            detail = request.POST['Detail']
            images = request.FILES.getlist('images')
            from_question = Question.objects.get(id=request.POST['comment'])
            answerer = Account.objects.get(user=user)
            answer=Answer.objects.create(detail = detail, from_question=from_question, answerer=answerer)
            for image in images:
                AnswerFile.objects.create(answer=answer, image=image)
            
            if not from_question.asker == answerer:
                Notification.objects.get(account=from_question.asker).reply_notification.add(answer)
                
        elif request.POST.get('reply'):
            detail = request.POST['Detail']
            images = request.FILES.getlist('images')
            from_answer = Answer.objects.get(id=request.POST['reply'])
            reply_answerer = Account.objects.get(user=user)
            reply_answer = ReplyAnswer.objects.create(detail = detail, from_answer=from_answer, reply_answerer=reply_answerer)
            for image in images:
                ReplyAnswerFile.objects.create(reply_answer=reply_answer, image=image)

        elif request.POST.get('fav'):
            question = Question.objects.get(id=question_id)
            account.fav_question.add(question)
            account.save()
            question.faved = question.fav_account.count()
            question.save()

        elif request.POST.get('unfav'):
            question = Question.objects.get(id=question_id)
            account.fav_question.remove(question)
            account.save()
            question.faved = question.fav_account.count()
            question.save()
    
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
    reply_notifications = notification.reply_notification.all().order_by('-date_answered')
    
    if request.user.is_staff:
        notification.qreport_notification_count = notification.qreport_notification.count()
        notification.areport_notification_count = notification.areport_notification.count()
        notification.rreport_notification_count = notification.rreport_notification.count()
        notification.save()

        qreport_notifications =  notification.qreport_notification.all().order_by('-date_asked')
        areport_notifications =  notification.areport_notification.all().order_by('-date_answered')
        rreport_notifications =  notification.rreport_notification.all().order_by('-date_reply_answered')
        return render(request, 'questionic/notification.html', {
            "notification_alert": notification_alert,
            "reply_notifications": reply_notifications,
            "qreport_notifications": qreport_notifications,
            "areport_notifications": areport_notifications,
            "rreport_notifications": rreport_notifications,
            "account": account,
            "time_now": datetime.now()
        })
    else:
        return render(request, 'questionic/notification.html', {
            "notification_alert": notification_alert,
            "reply_notifications": reply_notifications,
            "account": account,
            "time_now": datetime.now()
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

def report(request, type_report, report_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:login'))

    staff = User.objects.filter(is_staff=True)
    if type_report == 'question':
        question = Question.objects.get(id=report_id)
        question.reporter.add(request.user.id)
        for person in staff:
            account = Account.objects.get(user=person)
            Notification.objects.get(account=account).qreport_notification.add(question)

        return HttpResponseRedirect(reverse('questionic:question', args=(question.id, )))

    elif type_report == 'answer':
        answer = Answer.objects.get(id=report_id)
        answer.reporter.add(request.user.id)
        for person in staff:
            account = Account.objects.get(user=person)
            Notification.objects.get(account=account).areport_notification.add(answer)
        return HttpResponseRedirect(reverse('questionic:question', args=(answer.from_question.id, )))

    elif type_report == 'reply':
        reply = ReplyAnswer.objects.get(id=report_id)
        reply.reporter.add(request.user.id)
        for person in staff:
            account = Account.objects.get(user=person)
            Notification.objects.get(account=account).rreport_notification.add(reply)
        
        return HttpResponseRedirect(reverse('questionic:question', args=(reply.from_answer.from_question.id, )))
