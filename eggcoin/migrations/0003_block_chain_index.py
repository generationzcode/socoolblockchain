# Generated by Django 3.1.5 on 2021-05-26 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eggcoin', '0002_auto_20210526_0238'),
    ]

    operations = [
        migrations.AddField(
            model_name='block_chain',
            name='index',
            field=models.CharField(default=1, max_length=1000000),
            preserve_default=False,
        ),
    ]