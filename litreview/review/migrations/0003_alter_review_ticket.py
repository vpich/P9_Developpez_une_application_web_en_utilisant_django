# Generated by Django 4.1.7 on 2023-04-15 14:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0002_alter_ticket_time_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='ticket',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='review.ticket'),
        ),
    ]
