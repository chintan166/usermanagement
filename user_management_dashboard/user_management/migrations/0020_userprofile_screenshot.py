# Generated by Django 4.2.17 on 2025-01-25 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0019_quiz_area_of_interest'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='screenshot',
            field=models.ImageField(blank=True, null=True, upload_to='screenshots/'),
        ),
    ]
