# Generated by Django 4.1.3 on 2024-02-05 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_alter_customuser_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="deleted",
            field=models.BooleanField(default=False),
        ),
    ]
