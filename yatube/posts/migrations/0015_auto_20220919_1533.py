# Generated by Django 2.2.6 on 2022-09-19 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20220919_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(error_messages={'null': 'А кто поле будет заполнять? Пушкин?'}),
        ),
    ]