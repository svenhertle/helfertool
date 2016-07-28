# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-09 09:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0006_badgedefaults_no_default_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgesettings',
            name='language',
            field=models.CharField(choices=[('de', 'German'), ('en', 'English')], default='de', max_length=10, verbose_name='Language of badges'),
        ),
    ]