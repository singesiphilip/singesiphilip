# Generated by Django 4.2.3 on 2023-07-12 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='screenshot',
            field=models.ImageField(default='img/philip.jpg', upload_to='screenshot'),
        ),
    ]
