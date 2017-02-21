# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('StudentApp', '0003_remove_classroom_teacher_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='teacher_user',
            field=models.CharField(default=b'', max_length=500),
        ),
    ]
