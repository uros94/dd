# Generated by Django 3.0.4 on 2020-04-04 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_auto_20200402_2221'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='text',
            new_name='comment',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='approved_comment',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='author',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='created_date',
        ),
        migrations.AddField(
            model_name='comment',
            name='date',
            field=models.CharField(default=0, max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='semantics',
            field=models.CharField(default=0, max_length=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.CharField(default=0, max_length=60),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Post',
        ),
    ]
