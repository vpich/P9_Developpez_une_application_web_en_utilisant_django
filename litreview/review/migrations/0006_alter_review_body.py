# Generated by Django 4.1.7 on 2023-04-20 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0005_alter_review_ticket'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='body',
            field=models.TextField(blank=True, max_length=8192),
        ),
    ]
