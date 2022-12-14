from unicodedata import category
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Tag(models.Model):
    name = models.CharField(max_length=64, primary_key=True)

    def __str__(self):
        return f"{self.name}"

def user_directory_path(instance, filename):
    return 'image/account/user_{0}/{1}'.format(instance.user.id, filename)

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_profile = models.ImageField(upload_to = user_directory_path, blank=True)
    fav_tag = models.ManyToManyField(Tag, blank=True, related_name="fav_tag")
    fav_question = models.ManyToManyField('Question', blank=True, related_name="fav_account")
    following = models.ManyToManyField('Account', blank=True, related_name="follower")

    def __str__(self):
        return f"{self.user.username}"

class Question(models.Model):
    tags = models.ManyToManyField(Tag, blank=True, related_name="tags")
    title = models.CharField(max_length=128)
    detail = models.CharField(max_length=9999)
    category = models.CharField(max_length=64)
    grade = models.CharField(max_length=64)
    date_asked = models.DateTimeField('Date Asked', auto_now_add=True)
    asker = models.ForeignKey(Account, on_delete=models.CASCADE)
    reporter = models.ManyToManyField(Account, blank=True, related_name="question_report")
    faved = models.PositiveIntegerField(default=0)
    answer_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"question: {self.id}"

def question_directory_path(instance, filename):
    return 'images/question/question{0}_no{1}.{2}'.format(instance.question.id, instance.question.images.count(), filename.split('.')[-1])

class QuestionFile(models.Model):
    image = models.FileField(upload_to = question_directory_path, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='images')

class Answer(models.Model):
    detail = models.CharField(max_length=1024)
    date_answered = models.DateTimeField('Date Answered', auto_now_add=True)
    from_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answer")
    answerer = models.ForeignKey(Account, on_delete=models.CASCADE)
    reporter = models.ManyToManyField(Account, blank=True, related_name="answer_report")

    def __str__(self):
        return f"answer: {self.id} from {self.from_question}"

def answer_directory_path(instance, filename):
    return ('images/answer/question{0}_answer{1}_no{2}.{3}'
            .format(instance.answer.from_question.id, instance.answer.id, instance.answer.images.count(), filename.split('.')[-1]))

class AnswerFile(models.Model):
    image = models.FileField(upload_to = answer_directory_path, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='images')

class ReplyAnswer(models.Model):
    detail = models.CharField(max_length=1024) 
    date_reply_answered = models.DateTimeField('Date Reply Answered', auto_now_add=True)
    from_answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    reply_answerer = models.ForeignKey(Account, on_delete=models.CASCADE)
    reporter = models.ManyToManyField(Account, blank=True, related_name="reply_report")

    def __str__(self):
        return f"reply_answer: {self.id} from {self.from_answer}"

def reply_answer_directory_path(instance, filename):
    return ('images/reply_answer/question{0}_answer{1}_replyanswer{2}_no{3}.{4}'
            .format(instance.reply_answer.from_answer.from_question.id, instance.reply_answer.from_answer.id,
            instance.reply_answer.id, instance.reply_answer.images.count(), filename.split('.')[-1]))

class ReplyAnswerFile(models.Model):
    image = models.FileField(upload_to = reply_answer_directory_path, blank=True)
    reply_answer = models.ForeignKey(ReplyAnswer, on_delete=models.CASCADE, related_name='images')

class Notification(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='notifications')
    
    follow_notification = models.ManyToManyField(Question, blank=True, related_name='noti_follow')
    reply_notification = models.ManyToManyField(Answer, blank=True, related_name='noti_reply')
    qreport_notification = models.ManyToManyField(Question, blank=True, related_name='noti_qreport')
    areport_notification = models.ManyToManyField(Answer, blank=True, related_name='noti_areport')
    rreport_notification = models.ManyToManyField(ReplyAnswer, blank=True, related_name='noti_rreport')

    follow_notification_count = models.PositiveIntegerField(default=0)
    reply_notification_count = models.PositiveIntegerField(default=0)
    qreport_notification_count = models.PositiveIntegerField(default=0)
    areport_notification_count = models.PositiveIntegerField(default=0)
    rreport_notification_count = models.PositiveIntegerField(default=0)

    def alert_follow_notification(self):
        dotcount = self.follow_notification.count()
        count = self.follow_notification_count
        return dotcount - count

    def alert_reply_notification(self):
        dotcount = self.reply_notification.count()
        count = self.reply_notification_count
        return dotcount - count

    def alert_qreport_notification(self):
        dotcount = self.qreport_notification.count()
        count = self.qreport_notification_count
        return dotcount - count

    def alert_areport_notification(self):
        dotcount = self.areport_notification.count()
        count = self.areport_notification_count
        return dotcount - count

    def alert_rreport_notification(self):
        dotcount = self.rreport_notification.count()
        count = self.rreport_notification_count
        return dotcount - count

    def alert_notification(self):
        count_noti = self.alert_follow_notification() + self.alert_reply_notification() + self.alert_qreport_notification() + self.alert_areport_notification() + self.alert_rreport_notification()
        if count_noti != 0:
            return count_noti
        return 0

