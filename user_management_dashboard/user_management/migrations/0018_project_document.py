# Generated by Django 4.2.17 on 2025-01-24 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0017_project_document_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to='projects/'),
        ),
    ]
