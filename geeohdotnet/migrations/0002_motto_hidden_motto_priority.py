# Generated by Django 5.0.3 on 2024-04-10 15:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("geeohdotnet", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="motto",
            name="hidden",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="motto",
            name="priority",
            field=models.BooleanField(default=False),
        ),
    ]
