# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-26 09:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aminoApp', '0013_auto_20161224_1359'),
    ]

    operations = [
        migrations.CreateModel(
            name='LiteratureReference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('in_text', models.CharField(max_length=100)),
                ('reference_APA', models.CharField(max_length=500)),
                ('abstract', models.TextField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('category', models.CharField(blank=True, max_length=30, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='questionanswer',
            name='category',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
