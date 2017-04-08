# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-04-08 20:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_oldlinks'),
    ]

    operations = [
        migrations.AddField(
            model_name='oldlinks',
            name='token',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='oldlinks',
            name='user',
            field=models.CharField(max_length=100),
        ),
    ]