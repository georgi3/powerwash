from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import path
from django.template.response import TemplateResponse

from .models import ServicePricing, Customer, Quote

# @admin.register(ServicePricing)
class ServicePricingAdmin(admin.ModelAdmin):
    """Admin configuration for ServicePricing model"""
    list_display = (
        'name',
        'house_sqft_price',
        'driveway_sqft_price',
        'driveway_car_price',
        'patio_deck_sqft_price',
        'roof_cleaning_sqft_price',
        'gutter_cleaning_flat_price',
        'distance_price_per_km',
        'is_active',
        'updated_at'
    )
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('House & Driveway Pricing', {
            'fields': ('house_sqft_price', 'driveway_sqft_price', 'driveway_car_price')
        }),
        ('Outdoor Areas Pricing', {
            'fields': ('patio_deck_sqft_price', 'roof_cleaning_sqft_price', 'gutter_cleaning_flat_price')
        }),
        ('Travel Pricing', {
            'fields': ('distance_price_per_km',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# @admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin configuration for Customer model"""
    list_display = (
        'full_name',
        'email',
        'phone_number',
        'full_address',
        'created_at'
    )
    list_filter = ('state', 'city', 'created_at')
    search_fields = (
        'first_name',
        'last_name',
        'email',
        'phone_number',
        'address_line1',
        'city',
        'state',
        'zip_code'
    )
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'zip_code')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = "Customer Name"


class QuoteInline(admin.TabularInline):
    """Inline admin for Quote related to Customer"""
    model = Quote
    extra = 0
    fields = ('quote_number', 'quote_date', 'work_date', 'total_amount', 'is_completed')
    readonly_fields = ('quote_number', 'total_amount')
    show_change_link = True
    can_delete = False


# @admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    """Admin configuration for Quote model"""
    list_display = (
        'quote_number',
        'customer_name',
        'quote_date',
        'work_date',
        'total_amount',
        'distance_km',
        'status_tag',
        'created_at'
    )
    list_filter = (
        'is_completed',
        'quote_date',
        'work_date',
        'driveway_calculation_type',
        'gutter_cleaning',
        'created_at'
    )
    search_fields = (
        'quote_number',
        'customer__first_name',
        'customer__last_name',
        'customer__email',
        'notes'
    )
    readonly_fields = ('created_at', 'updated_at', 'total_amount')
    autocomplete_fields = ['customer']

    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'pricing', 'quote_number', 'quote_date', 'work_date', 'is_completed')
        }),
        ('House & Driveway Details', {
            'fields': ('house_sqft', 'driveway_calculation_type', 'driveway_sqft', 'driveway_cars')
        }),
        ('Other Services', {
            'fields': ('patio_deck_sqft', 'roof_cleaning_sqft', 'gutter_cleaning', 'distance_km')
        }),
        ('Quote Total', {
            'fields': ('total_amount', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def customer_name(self, obj):
        return obj.customer.full_name

    customer_name.short_description = "Customer"

    def status_tag(self, obj):
        if obj.is_completed:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 10px;">Completed</span>')
        elif obj.work_date and obj.work_date < timezone.now().date():
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 10px;">Overdue</span>')
        elif obj.work_date:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 10px; border-radius: 10px;">Scheduled</span>')
        else:
            return format_html(
                '<span style="background-color: #17a2b8; color: white; padding: 3px 10px; border-radius: 10px;">Quote</span>')

    status_tag.short_description = "Status"

    # Add customer info to the Quote admin
    def get_queryset(self, request):
        """Prefetch related customer to avoid extra queries"""
        return super().get_queryset(request).select_related('customer', 'pricing')

    # Add customer's quotes to customer view
    CustomerAdmin.inlines = [QuoteInline]


class AdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('price-calculator/', self.admin_view(self.price_calculator_view), name='price-calculator'),
        ]
        return custom_urls + urls

    def price_calculator_view(self, request):
        # Get the latest pricing configuration to pass to the template
        pricing = ServicePricing.objects.filter(is_active=True).first()

        # Fallback to the most recently updated pricing if no active pricing exists
        if not pricing:
            pricing = ServicePricing.objects.order_by('-updated_at').first()

        # Create the context with the pricing data
        context = {
            **self.each_context(request),
            'title': 'Price Calculator',
            'pricing': pricing,
        }

        # Render the template with the context
        return TemplateResponse(request, 'admin/price_calculator.html', context)


# Replace the default admin site
admin.site = AdminSite()

# Register your models with admin
admin.site.register(ServicePricing, ServicePricingAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.site_header = 'Capital Power Washer Admin'
admin.site.site_title = 'Capital Power Washer Admin Portal'
admin.site.index_title = 'Welcome to Capital Power Washing Admin Portal'
