# Generated by Django 5.1.4 on 2025-01-04 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_user_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
