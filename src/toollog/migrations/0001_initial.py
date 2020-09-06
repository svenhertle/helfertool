# Generated by Django 3.1.1 on 2020-09-05 18:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('registration', '0043_auto_20200409_1711'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(verbose_name='Timestamp')),
                ('level', models.CharField(max_length=16, verbose_name='Log level')),
                ('message', models.CharField(max_length=512, verbose_name='Message')),
                ('extras', models.JSONField(blank=True, null=True, verbose_name='Extra data')),
                ('module', models.CharField(max_length=128, verbose_name='Helfertool module')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='registration.event', verbose_name='Event')),
                ('helper', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='registration.helper', verbose_name='Helper')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='helfertoollogentry', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]