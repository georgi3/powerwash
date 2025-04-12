from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class ServicePricing(models.Model):
    """
    Model to store pricing configuration for all services
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    # House square footage pricing
    house_sqft_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.50'),
        verbose_name="House Price per Square Foot"
    )

    # Driveway pricing
    driveway_sqft_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.70'),
        verbose_name="Driveway Price per Square Foot"
    )
    driveway_car_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('50.00'),
        verbose_name="Driveway Price per Car"
    )

    # Patio/Deck pricing
    patio_deck_sqft_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.80'),
        verbose_name="Patio/Deck Price per Square Foot"
    )

    # Roof cleaning pricing
    roof_cleaning_sqft_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.60'),
        verbose_name="Roof Cleaning Price per Square Foot"
    )

    # Gutter cleaning pricing
    gutter_cleaning_flat_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal('75.00'),
        verbose_name="Gutter Cleaning Flat Price"
    )

    # Distance pricing
    distance_price_per_km = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('2.00'),
        verbose_name="Price per Kilometer"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Service Pricing"
        verbose_name_plural = "Service Pricing"

    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"


class Customer(models.Model):
    """
    Model to store customer information
    """
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address_line1 = models.CharField(max_length=255, verbose_name="Address Line 1")
    address_line2 = models.CharField(max_length=255, blank=True, verbose_name="Address Line 2")
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_address(self):
        address = f"{self.address_line1}"
        if self.address_line2:
            address += f", {self.address_line2}"
        address += f", {self.city}, {self.state} {self.zip_code}"
        return address


class Quote(models.Model):
    """
    Model to store quotes created for customers
    """
    DRIVEWAY_CALCULATION_CHOICES = [
        ('sqft', 'Square Footage'),
        ('cars', 'Number of Cars'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='quotes'
    )

    pricing = models.ForeignKey(
        ServicePricing,
        on_delete=models.PROTECT,
        related_name='quotes'
    )

    # Quote details
    quote_number = models.CharField(max_length=50, unique=True)
    quote_date = models.DateField(default=timezone.now)
    work_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    # Service areas and measurements
    house_sqft = models.PositiveIntegerField(
        default=0,
        verbose_name="House Square Footage"
    )

    # Driveway options
    driveway_calculation_type = models.CharField(
        max_length=4,
        choices=DRIVEWAY_CALCULATION_CHOICES,
        default='sqft',
        verbose_name="Driveway Calculation Method"
    )
    driveway_sqft = models.PositiveIntegerField(
        default=0,
        verbose_name="Driveway Square Footage"
    )
    driveway_cars = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(5)],
        verbose_name="Number of Cars (Driveway)"
    )

    # Other service areas
    patio_deck_sqft = models.PositiveIntegerField(
        default=0,
        verbose_name="Patio/Deck Square Footage"
    )
    roof_cleaning_sqft = models.PositiveIntegerField(
        default=0,
        verbose_name="Roof Cleaning Square Footage"
    )
    gutter_cleaning = models.BooleanField(
        default=False,
        verbose_name="Include Gutter Cleaning"
    )
    distance_km = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Distance to Job (km)"
    )

    # Quote totals
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Quote Amount"
    )

    # Other quote info
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quote"
        verbose_name_plural = "Quotes"
        ordering = ['-quote_date']

    def __str__(self):
        return f"Quote #{self.quote_number} - {self.customer.full_name}"

    def save(self, *args, **kwargs):
        # Calculate the total amount before saving
        if not self.total_amount:
            self.calculate_total()
        super().save(*args, **kwargs)

    def calculate_total(self):
        """Calculate the total amount based on service selections and pricing"""
        total = Decimal('0.00')

        # House
        total += Decimal(str(self.house_sqft)) * self.pricing.house_sqft_price

        # Driveway
        if self.driveway_calculation_type == 'sqft':
            total += Decimal(str(self.driveway_sqft)) * self.pricing.driveway_sqft_price
        else:  # 'cars'
            total += Decimal(str(self.driveway_cars)) * self.pricing.driveway_car_price

        # Patio/Deck
        total += Decimal(str(self.patio_deck_sqft)) * self.pricing.patio_deck_sqft_price

        # Roof Cleaning
        total += Decimal(str(self.roof_cleaning_sqft)) * self.pricing.roof_cleaning_sqft_price

        # Gutter Cleaning
        if self.gutter_cleaning:
            total += self.pricing.gutter_cleaning_flat_price

        # Distance
        total += Decimal(str(self.distance_km)) * self.pricing.distance_price_per_km

        self.total_amount = total
        return total