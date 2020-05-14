# Generated by Django 2.2.4 on 2020-04-20 13:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bad_influence', '0012_delete_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bad_influence.Player')),
            ],
        ),
    ]
