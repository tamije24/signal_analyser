# Generated by Django 5.1 on 2024-08-29 09:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comtrade_reader', '0016_remove_timesignal_file_delete_analogsignal_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='analogchannel',
            old_name='comtrade_channel_id',
            new_name='id',
        ),
    ]
