# Generated by Django 4.2.17 on 2025-01-25 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0021_remove_userprofile_screenshot_customuser_screenshot'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
