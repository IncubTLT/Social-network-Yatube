# Generated by Django 2.2.6 on 2022-09-16 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20220916_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(error_messages={'null': 'А кто поле будет заполнять, Пушкин?'}),
        ),
    ]