# Generated by Django 4.1.5 on 2023-02-02 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskApp', '0008_task_priority'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='check_status',
            field=models.BooleanField(default='', null=True),
        ),
    ]
