from django.contrib import admin
from .models import Tag, Account, Question, Answer, ReplyAnswer
from .models import QuestionFile, AnswerFile, ReplyAnswerFile, Notification

# Register your models here.

class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)

class AccountAdmin(admin.ModelAdmin):
    list_display = ("user", "image_profile")
    filter_horizontal = ("fav_tag", "following", "report", "fav_question")

class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "detail", "category", "grade", "date_asked", "asker", "faved", "answer_count")
    filter_horizontal = ("tags", "reporter")

class AnswerAdmin(admin.ModelAdmin):
    list_display = ("detail", "date_answered", "from_question", "answerer")
    filter_horizontal = ("reporter",)

class ReplyAnswerAdmin(admin.ModelAdmin):
    list_display = ("detail", "date_reply_answered", "from_answer", "reply_answerer")
    filter_horizontal = ("reporter",)

class QuestionFileAdmin(admin.ModelAdmin):
    list_display = ("image", "question")

class AnswerFileAdmin(admin.ModelAdmin):
    list_display = ("image", "answer")

class ReplyAnswerFileAdmin(admin.ModelAdmin):
    list_display = ("image", "reply_answer")

class NotificationAdmin(admin.ModelAdmin):
    list_display = ("account", "follow_notification_count", "reply_notification_count")
    filter_horizontal = ("follow_notification", "reply_notification", "qreport_notification", "areport_notification", "rreport_notification")

admin.site.register(Tag, TagAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(ReplyAnswer, ReplyAnswerAdmin)
admin.site.register(QuestionFile, QuestionFileAdmin)
admin.site.register(AnswerFile, AnswerFileAdmin)
admin.site.register(ReplyAnswerFile, ReplyAnswerFileAdmin)
admin.site.register(Notification, NotificationAdmin)