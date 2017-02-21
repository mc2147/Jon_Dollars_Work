# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StudentApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoodDeed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cost', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=1000)),
                ('id_num', models.IntegerField(default=0)),
                ('defined', models.BooleanField(default=False)),
                ('created', models.BooleanField(default=False)),
                ('class_name', models.CharField(default=b'', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Reward',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cost', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=1000)),
                ('id_num', models.IntegerField(default=0)),
                ('class_name', models.CharField(default=b'', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='SpendRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rewardname', models.CharField(default=b'', max_length=500)),
                ('number', models.IntegerField(default=0)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('class_name', models.CharField(default=b'', max_length=500)),
                ('student', models.OneToOneField(to='StudentApp.Student')),
                ('teacher', models.OneToOneField(to='StudentApp.Teacher')),
            ],
        ),
        migrations.AddField(
            model_name='teacher',
            name='GDs',
            field=models.ManyToManyField(to='StudentApp.GoodDeed'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='Rewards',
            field=models.ManyToManyField(to='StudentApp.Reward'),
        ),
    ]
