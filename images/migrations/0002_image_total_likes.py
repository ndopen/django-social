# Generated by Django 4.0.7 on 2022-12-01 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='total_likes',
            field=models.PositiveBigIntegerField(db_index=True, default=0),
        ),
    ]