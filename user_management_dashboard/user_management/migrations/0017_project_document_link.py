# Generated by Django 4.2.17 on 2025-01-24 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0016_remove_project_is_approved_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='document_link',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
