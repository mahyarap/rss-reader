# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-06-29 10:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0002_feed_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feed',
            name='priority',
            field=models.IntegerField(db_index=True),
        ),
    ]
