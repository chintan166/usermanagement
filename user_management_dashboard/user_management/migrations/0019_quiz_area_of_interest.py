# Generated by Django 4.2.17 on 2025-01-24 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0018_project_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='area_of_interest',
            field=models.CharField(choices=[('Django', 'Django'), ('Machine Learning', 'Machine Learning'), ('AI', 'AI'), ('Laravel', 'Laravel'), ('React', 'React')], max_length=100, null=True),
        ),
    ]
