# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-19 20:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aminoApp', '0004_auto_20161012_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='food',
            name='food_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='link',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]