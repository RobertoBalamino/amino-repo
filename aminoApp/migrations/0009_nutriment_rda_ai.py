# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-27 19:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aminoApp', '0008_foodcategory_address_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='nutriment',
            name='RDA_AI',
            field=models.FloatField(null=True),
        ),
    ]