# Generated by Django 4.2.17 on 2025-01-25 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0025_submission_admin_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='certificate',
            field=models.ImageField(blank=True, null=True, upload_to='certificates/'),
        ),
    ]
