# Generated by Django 4.1.5 on 2023-02-02 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskApp', '0009_task_check_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='check_status',
            field=models.BooleanField(default=0),
        ),
    ]
