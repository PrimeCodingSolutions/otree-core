# Generated by Django 2.2.4 on 2020-04-15 10:36

from django.db import migrations
import otree.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('bad_influence', '0006_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='chat_color',
            field=otree.db.models.LongStringField(null=True),
        ),
    ]
