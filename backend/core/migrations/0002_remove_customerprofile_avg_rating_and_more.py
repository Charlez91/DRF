# Generated by Django 4.1.3 on 2024-01-29 13:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("ecommerce", "0002_category_parent_item_specifications_and_more"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="customerprofile", name="avg_rating",),
        migrations.AddField(
            model_name="customuser",
            name="avg_rating",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=4),
        ),
        migrations.AlterField(
            model_name="customerprofile",
            name="user_type",
            field=models.CharField(
                choices=[("vendor", "VENDOR"), ("buyer", "BUYER")],
                default="buyer",
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=250)),
                ("email", models.EmailField(max_length=254)),
                ("comment", models.TextField(blank=True, null=True)),
                (
                    "date_created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("approved", models.BooleanField(default=True)),
                ("rating", models.DecimalField(decimal_places=2, max_digits=4)),
                (
                    "item",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="ecommerce.item",
                    ),
                ),
                (
                    "vendor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Comment",
                "verbose_name_plural": "Comments",
                "ordering": ("-date_created",),
            },
        ),
    ]