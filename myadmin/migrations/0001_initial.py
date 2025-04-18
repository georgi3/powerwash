# Generated by Django 5.2 on 2025-04-11 23:07

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Customer",
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
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254)),
                ("phone_number", models.CharField(max_length=20)),
                (
                    "address_line1",
                    models.CharField(max_length=255, verbose_name="Address Line 1"),
                ),
                (
                    "address_line2",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Address Line 2"
                    ),
                ),
                ("city", models.CharField(max_length=100)),
                ("state", models.CharField(max_length=100)),
                ("zip_code", models.CharField(max_length=20)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Customer",
                "verbose_name_plural": "Customers",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ServicePricing",
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
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
                (
                    "house_sqft_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.50"),
                        max_digits=5,
                        verbose_name="House Price per Square Foot",
                    ),
                ),
                (
                    "driveway_sqft_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.70"),
                        max_digits=5,
                        verbose_name="Driveway Price per Square Foot",
                    ),
                ),
                (
                    "driveway_car_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("50.00"),
                        max_digits=6,
                        verbose_name="Driveway Price per Car",
                    ),
                ),
                (
                    "patio_deck_sqft_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.80"),
                        max_digits=5,
                        verbose_name="Patio/Deck Price per Square Foot",
                    ),
                ),
                (
                    "roof_cleaning_sqft_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.60"),
                        max_digits=5,
                        verbose_name="Roof Cleaning Price per Square Foot",
                    ),
                ),
                (
                    "gutter_cleaning_flat_price",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("75.00"),
                        max_digits=6,
                        verbose_name="Gutter Cleaning Flat Price",
                    ),
                ),
                (
                    "distance_price_per_km",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("2.00"),
                        max_digits=5,
                        verbose_name="Price per Kilometer",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Service Pricing",
                "verbose_name_plural": "Service Pricing",
            },
        ),
        migrations.CreateModel(
            name="Quote",
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
                ("quote_number", models.CharField(max_length=50, unique=True)),
                ("quote_date", models.DateField(default=django.utils.timezone.now)),
                ("work_date", models.DateField(blank=True, null=True)),
                ("is_completed", models.BooleanField(default=False)),
                (
                    "house_sqft",
                    models.PositiveIntegerField(
                        default=0, verbose_name="House Square Footage"
                    ),
                ),
                (
                    "driveway_calculation_type",
                    models.CharField(
                        choices=[
                            ("sqft", "Square Footage"),
                            ("cars", "Number of Cars"),
                        ],
                        default="sqft",
                        max_length=4,
                        verbose_name="Driveway Calculation Method",
                    ),
                ),
                (
                    "driveway_sqft",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Driveway Square Footage"
                    ),
                ),
                (
                    "driveway_cars",
                    models.PositiveSmallIntegerField(
                        default=0,
                        validators=[django.core.validators.MaxValueValidator(5)],
                        verbose_name="Number of Cars (Driveway)",
                    ),
                ),
                (
                    "patio_deck_sqft",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Patio/Deck Square Footage"
                    ),
                ),
                (
                    "roof_cleaning_sqft",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Roof Cleaning Square Footage"
                    ),
                ),
                (
                    "gutter_cleaning",
                    models.BooleanField(
                        default=False, verbose_name="Include Gutter Cleaning"
                    ),
                ),
                (
                    "distance_km",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="Distance to Job (km)"
                    ),
                ),
                (
                    "total_amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        verbose_name="Total Quote Amount",
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quotes",
                        to="myadmin.customer",
                    ),
                ),
                (
                    "pricing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="quotes",
                        to="myadmin.servicepricing",
                    ),
                ),
            ],
            options={
                "verbose_name": "Quote",
                "verbose_name_plural": "Quotes",
                "ordering": ["-quote_date"],
            },
        ),
    ]
