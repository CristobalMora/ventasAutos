# Generated by Django 4.2.1 on 2024-05-11 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miapp', '0002_cliente_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$600000$AoAC1YnoEQJEPCfGOrxafa$ZZn0DqW9MDdo1nEf4AdM7HyoPCBcvSO8IyMbs79WTEs=', max_length=128),
        ),
    ]
