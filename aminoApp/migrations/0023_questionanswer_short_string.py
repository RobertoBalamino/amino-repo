# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-04 13:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aminoApp', '0022_questionanswer_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionanswer',
            name='short_string',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]