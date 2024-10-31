# Generated by Django 5.1.2 on 2024-10-28 20:02

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_category_alter_event_options_remove_event_created_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RemoveField(
            model_name='event',
            name='category',
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['date']},
        ),
        migrations.RemoveField(
            model_name='event',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='event',
            name='location',
        ),
        migrations.RemoveField(
            model_name='event',
            name='organizer',
        ),
        migrations.RemoveField(
            model_name='event',
            name='priority',
        ),
        migrations.RemoveField(
            model_name='event',
            name='start_date',
        ),
        migrations.AddField(
            model_name='event',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='event',
            name='time',
            field=models.TimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(),
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.event')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.participant')),
            ],
            options={
                'ordering': ['timestamp'],
                'unique_together': {('event', 'participant')},
            },
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]
