# Generated by Django 5.1 on 2024-08-21 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comtrade_reader', '0006_alter_analogchannel_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analogchannel',
            name='channel_id',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
    ]
