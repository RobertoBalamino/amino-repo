# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-14 12:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aminoApp', '0023_questionanswer_short_string'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='aa_score',
            field=models.TextField(blank=True, null=True),
        ),
    ]
