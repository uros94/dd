# Generated by Django 3.0.4 on 2020-04-26 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_auto_20200415_1858'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='similarUsers',
        ),
        migrations.AddField(
            model_name='profile',
            name='terminal',
            field=models.CharField(blank=True, max_length=1600),
        ),
    ]
