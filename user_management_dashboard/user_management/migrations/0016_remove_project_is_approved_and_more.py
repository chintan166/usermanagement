# Generated by Django 4.2.17 on 2025-01-24 14:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0015_project_is_approved_submission_certificate_file_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='is_approved',
        ),
        migrations.RemoveField(
            model_name='submission',
            name='certificate_file',
        ),
        migrations.RemoveField(
            model_name='submission',
            name='is_approved',
        ),
    ]
