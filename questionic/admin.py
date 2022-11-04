from django.contrib import admin
from .models import Tag, Account, Question, Answer, ReplyAnswer
from .models import QuestionFile, AnswerFile, ReplyAnswerFile

# Register your models here.

class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)

class AccountAdmin(admin.ModelAdmin):
    list_display = ("user", "image_profile")
    filter_horizontal = ("fav_tag", "following", "report")

class QuestionAdmin(admin.ModelAdmin):
    list_display = ("title", "detail", "category", "grade", "date_asked", "asker")
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

admin.site.register(Tag, TagAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(ReplyAnswer, ReplyAnswerAdmin)
admin.site.register(QuestionFile, QuestionFileAdmin)
admin.site.register(AnswerFile, AnswerFileAdmin)
admin.site.register(ReplyAnswerFile, ReplyAnswerFileAdmin)