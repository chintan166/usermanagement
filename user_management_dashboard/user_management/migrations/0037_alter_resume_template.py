# Generated by Django 4.2.17 on 2025-01-29 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0036_resume_linkedin_resume_location_resume_website'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resume',
            name='template',
            field=models.CharField(choices=[('simple_layout', 'Simple Layout'), ('creative_layout', 'Creative Layout'), ('professional', 'professional')], max_length=50, null=True),
        ),
    ]
