# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-30 13:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aminoApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_name', models.CharField(max_length=200)),
                ('pub_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='date added')),
                ('food_category', models.IntegerField(null=True)),
                ('food_dbid', models.IntegerField(default=0)),
                ('efficiency', models.FloatField(null=True)),
                ('nutritional_value', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='aminoApp.NutritionalValue')),
            ],
            options={
                'ordering': ['food_name'],
            },
        ),
        migrations.CreateModel(
            name='FoodPair',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foodOneId', models.IntegerField()),
                ('foodTwoId', models.IntegerField()),
                ('pair_name', models.CharField(max_length=30, null=True)),
                ('bestEfficiency', models.FloatField(null=True)),
                ('bestProportion', models.FloatField(null=True)),
                ('angleAbsolute', models.FloatField(null=True)),
                ('angleIncomplete', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
                ('food', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='aminoApp.Food')),
            ],
        ),
        migrations.CreateModel(
            name='Nutriment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dbid', models.IntegerField()),
                ('internal_name', models.CharField(max_length=10)),
                ('public_name', models.CharField(max_length=20)),
                ('unit', models.CharField(max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('category', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('category', models.CharField(blank=True, max_length=15, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True, null=True, verbose_name='date added')),
                ('efficiency', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RelativeAminoScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField()),
                ('aminoAcid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aminoApp.Nutriment')),
                ('food', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='aminoApp.Food')),
            ],
        ),
        migrations.AddField(
            model_name='ingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aminoApp.Recipe'),
        ),
    ]