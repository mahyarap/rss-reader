# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-29 18:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0003_auto_20190629_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feed',
            name='priority',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]