# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-26 10:54
from __future__ import unicode_literals

from django.db import migrations, models
import uuid

def gen_uuid(apps, schema_editor):
    Person = apps.get_model('news', 'Person')
    for row in Person.objects.all():
        row.token = uuid.uuid4()
        row.save()



class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_person_token'),
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]