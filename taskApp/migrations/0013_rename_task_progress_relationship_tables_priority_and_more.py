# Generated by Django 4.1.5 on 2023-02-02 08:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taskApp', '0012_relationship_tables_task_progress'),
    ]

    operations = [
        migrations.RenameField(
            model_name='relationship_tables',
            old_name='task_progress',
            new_name='priority',
        ),
        migrations.RemoveField(
            model_name='task',
            name='priority',
        ),
    ]
