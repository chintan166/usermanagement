# Generated by Django 4.2.17 on 2025-01-27 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0028_remove_post_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='apply',
            field=models.CharField(help_text='URL or email to apply for the position', max_length=200, null=True),
        ),
    ]
