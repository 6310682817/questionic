# Generated by Django 4.1 on 2022-11-12 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionic', '0002_account_fav_question_account_report_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='fav_question',
            field=models.ManyToManyField(blank=True, related_name='fav_question', to='questionic.question'),
        ),
        migrations.AlterField(
            model_name='question',
            name='detail',
            field=models.CharField(max_length=9999),
        ),
    ]
