# Generated by Django 5.1.6 on 2025-03-06 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_alter_tag_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Not Started', max_length=15),
        ),
    ]
