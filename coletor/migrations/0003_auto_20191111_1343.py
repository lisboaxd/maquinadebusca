# Generated by Django 2.2.6 on 2019-11-11 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coletor', '0002_auto_20191109_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='url',
            field=models.URLField(unique=True, verbose_name='Url'),
        ),
    ]