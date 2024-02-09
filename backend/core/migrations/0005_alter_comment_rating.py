# Generated by Django 4.1.3 on 2024-02-08 19:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_comment_deleted"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="rating",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=4,
                validators=[
                    django.core.validators.MinValueValidator(
                        1, message="Rating must not be less than 1"
                    )
                ],
            ),
        ),
    ]
