# Generated by Django 3.2.7 on 2024-12-12 16:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_follow_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='image',
        ),
    ]
