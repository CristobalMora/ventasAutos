# Generated by Django 5.0.6 on 2024-06-15 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miapp', '0008_alter_cliente_password_alter_producto_precio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='password',
            field=models.CharField(default='pbkdf2_sha256$720000$XMyGWSdI8DrR7eEIZKIgE8$FKWkvzHxPuWmJPuUnAcq2S2kVQt9ZBkrcSgJllYMNvQ=', max_length=128),
        ),
    ]
