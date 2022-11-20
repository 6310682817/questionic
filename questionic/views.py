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

        return render(request, 'questionic/index.html', {
            "question_lastest": question_lastest,
            "question_popular": question_popular,
            "time_now": datetime.now(),
        })

    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    notification = Notification.objects.get(account=account)
    notification_alert = notification.alert_notification()

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

    notification_alert = notification.alert_notification()
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

        follower = Account.objects.filter(following=user.id)
        for person in follower:
            Notification.objects.get(account=person).follow_notification.add(question)

        return HttpResponseRedirect(reverse('questionic:question', args=(question.id, ))) 
         
        
    notification_alert = notification.alert_notification()  
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
    notification_alert = notification.alert_notification()

    if request.method == 'POST':

        if  request.POST.get('comment'):
            detail = request.POST['Detail']
            images = request.FILES.getlist('images')
            from_question = Question.objects.get(id=request.POST['comment'])
            answerer = Account.objects.get(user=user)
            answer=Answer.objects.create(detail = detail, from_question=from_question, answerer=answerer)
            from_question.answer_count = from_question.answer.count()
            from_question.save()
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

def fav_question(request, question_id, status):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:login'))

    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    if status == 'fav':
        question = Question.objects.get(id=question_id)
        account.fav_question.add(question)
        account.save()
        question.faved = question.fav_account.count()
        question.save()

    elif status == 'unfav':
        question = Question.objects.get(id=question_id)
        account.fav_question.remove(question)
        account.save()
        question.faved = question.fav_account.count()
        question.save()
    
    return HttpResponseRedirect(reverse('questionic:question', args=(question_id, )))
    

def notification(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:login'))

    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    notification = Notification.objects.get(account=account)
    new_noti = {
        'reply': notification.alert_reply_notification(), 
        'follow': notification.alert_follow_notification(),
        'qreport': notification.alert_qreport_notification(), 
        'areport': notification.alert_areport_notification(), 
        'rreport': notification.alert_rreport_notification()
        }

    notification.reply_notification_count = notification.reply_notification.count()
    notification.follow_notification_count = notification.follow_notification.count()
    notification.save()
    
    notification_alert = notification.alert_notification()
    reply_notifications = notification.reply_notification.all().order_by('-date_answered')
    follow_notifications = notification.follow_notification.all().order_by('-date_asked')
    
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
            "new_noti": new_noti,
            "reply_notifications": reply_notifications,
            "follow_notifications": follow_notifications,
            "qreport_notifications": qreport_notifications,
            "areport_notifications": areport_notifications,
            "rreport_notifications": rreport_notifications,
            "account": account,
            "time_now": datetime.now()
        })
    else:
        return render(request, 'questionic/notification.html', {
            "notification_alert": notification_alert,
            "new_noti": new_noti,
            "reply_notifications": reply_notifications,
            "follow_notifications": follow_notifications,
            "account": account,
            "time_now": datetime.now()
        })

def search(request):
    if not request.user.is_authenticated:
        search_keyword = ""
        category = ""
        grade = ""
        status = ""
        if request.method == "GET":
            question_search = Question.objects.all()
            if request.GET.get('search_keyword'):
                search_keyword = request.GET['search_keyword']
                question_search = question_search.filter(Q(title__contains=search_keyword) | Q(detail__contains=search_keyword))
            if request.GET.get('category'):
                category = request.GET['category']
                question_search = question_search.filter(category=category)
            if request.GET.get('grade'):
                grade = request.GET['grade']
                question_search = question_search.filter(grade=grade)
            if request.GET.get('status'):
                status = request.GET['status']
                if status == 'unanswer':
                    question_search = question_search.filter(answer_count=0)
                elif status == 'answer':
                    question_search = question_search.exclude(answer_count=0)

        return render(request, 'questionic/search.html', {
            "search_keyword": search_keyword,
            "category": category,
            "grade": grade,
            "status": status,
            "question_search": question_search,
        })

    
    user = User.objects.get(username=request.user.username)
    account = Account.objects.get(user=user)
    notification = Notification.objects.get(account=account)
    notification_alert = notification.alert_notification()

    search_keyword = ""
    category = ""
    grade = ""
    status = ""
    if request.method == "GET":
        question_search = Question.objects.all()
        if request.GET.get('search_keyword'):
            search_keyword = request.GET['search_keyword']
            question_search = question_search.filter(Q(title__contains=search_keyword) | Q(detail__contains=search_keyword))
        if request.GET.get('category'):
            category = request.GET['category']
            question_search = question_search.filter(category=category)
        if request.GET.get('grade'):
            grade = request.GET['grade']
            question_search = question_search.filter(grade=grade)
        if request.GET.get('status'):
            status = request.GET['status']
            if status == 'unanswer':
                question_search = question_search.filter(answer_count=0)
            elif status == 'answer':
                question_search = question_search.exclude(answer_count=0)

    return render(request, 'questionic/search.html', {
        "notification_alert": notification_alert,
        "search_keyword": search_keyword,
        "category": category,
        "grade": grade,
        "status": status,
        "question_search": question_search,
        "account": account
    })

def notification_alert(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        account = Account.objects.get(user=user)
        notification = Notification.objects.get(account=account)
        notification_alert = notification.alert_notification()
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

def delete(request, type, id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users:login'))

    user = User.objects.get(username=request.user.username)
    if type == "question":
        question = Question.objects.get(id=id)
        
        if not user.is_staff and not question.asker.user == user:
            return HttpResponseRedirect(reverse('questionic:question', args=(question.id, )))

        question.delete()
    elif type == "answer":
        answer = Answer.objects.get(id=id)
        
        if not user.is_staff and not answer.answerer.user == user:
            return HttpResponseRedirect(reverse('questionic:question', args=(answer.from_question.id, )))

        answer.delete()
        return HttpResponseRedirect(reverse('questionic:question', args=(answer.from_question.id, )))

    elif type == "reply":
        reply_answer = ReplyAnswer.objects.get(id=id)
        
        if not user.is_staff and not reply_answer.reply_answerer.user == user:
            return HttpResponseRedirect(reverse('questionic:question', args=(reply_answer.from_answer.from_question.id, )))

        reply_answer.delete()
        return HttpResponseRedirect(reverse('questionic:question', args=(reply_answer.from_answer.from_question.id, )))

    return HttpResponseRedirect(reverse('questionic:index'))

