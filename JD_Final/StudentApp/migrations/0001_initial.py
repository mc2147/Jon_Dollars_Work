# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('class_num', models.IntegerField(default=0)),
                ('name', models.CharField(default=b'', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('custom_input', models.CharField(default=b'', max_length=1500)),
                ('g_deed', models.IntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.BooleanField(default=False)),
                ('class_name', models.CharField(default=b'', max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('points', models.IntegerField(default=0)),
                ('inventory_backup', models.CharField(default=b'', max_length=1000)),
                ('class_name', models.CharField(default=b'', max_length=500)),
                ('requests', models.ManyToManyField(to='StudentApp.Request')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('inbox_backup', models.CharField(default=b'', max_length=1000)),
                ('spendbox_backup', models.CharField(default=b'', max_length=1000)),
                ('classrooms', models.ManyToManyField(to='StudentApp.Classroom')),
                ('students', models.ManyToManyField(to='StudentApp.Student')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=100)),
                ('points', models.IntegerField(default=0)),
                ('members', models.ManyToManyField(to='StudentApp.Student')),
                ('teacher', models.OneToOneField(to='StudentApp.Teacher')),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='teacher_user',
            field=models.OneToOneField(to='StudentApp.Teacher'),
        ),
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='request',
            name='student_object',
            field=models.OneToOneField(to='StudentApp.Student'),
        ),
        migrations.AddField(
            model_name='request',
            name='teacher',
            field=models.OneToOneField(to='StudentApp.Teacher'),
        ),
        migrations.AddField(
            model_name='classroom',
            name='students',
            field=models.ManyToManyField(to='StudentApp.Student'),
        ),
        migrations.AddField(
            model_name='classroom',
            name='teacher_user',
            field=models.OneToOneField(to='StudentApp.Teacher'),
        ),
    ]
