from django.contrib import admin
from .models import MilkRecord, MilkSale, StockFeed, Animal, Breeding, FarmFinance, Employee


class MilkRecordAdmin(admin.ModelAdmin):
    list_display = (
        'milking_date', 
        'record_id',
        'cow_name', 
        'total_milk_quantity'
    )
    search_fields = ['record_id', 'cow_name']
    list_filter = ('milking_date',)

    def total_milk_quantity(self, obj):
        return obj.total_milk_quantity()

    total_milk_quantity.short_description = 'Total Milk Quantity'
    total_milk_quantity.admin_order_field = 'total_milk_quantity'

admin.site.register(MilkRecord, MilkRecordAdmin)

class MilkSaleAdmin(admin.ModelAdmin):
    list_display = (
        'current_date', 
        'client_name', 
        'amount_bought', 
        'total_price'
    )
    search_fields = ('client_name', 'client_contact')
    list_filter = ('current_date',)

admin.site.register(MilkSale, MilkSaleAdmin)


class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        'ear_tag', 
        'cow_name', 
        'animal_type', 
        'breed', 
        'color'
    )
    search_fields = ('ear_tag', 'cow_name',)
    list_filter = ('breed', 'color')
    
admin.site.register(Animal, AnimalAdmin)


class BreedingAdmin(admin.ModelAdmin):
    list_display = (
        'breeding_id',
        'cow_name',
        'bull_name',
        'calf_name',
        'breeding_date',
        'date_due_to_calve',
        'date_calved',
    )
    list_filter = ('breeding_date', 'date_due_to_calve', 'date_calved')
    search_fields = ('breeding_id', 'cow_name', 'bull_name', 'calf_name')
    readonly_fields = ('heat_date', 'breeding_id',)

    fieldsets = (
        ('Breeding Information', {
            'fields': ('heat_date', 'breeding_date', 'bull_name')
        }),
        ('Cow Information', {
            'fields': ('cow_name',)
        }),
        ('Pregnancy and Calving Information', {
            'fields': ('pregnancy_diagnosis_date', 'date_due_to_calve', 'date_calved', 'age_of_cow_at_calving')
        }),
        ('Calf Information', {
            'fields': ('calf_name', 'calf_id')
        }),
        ('Additional Notes', {
            'fields': ('calving_notes',)
        }),
    )

admin.site.register(Breeding, BreedingAdmin)

class FarmFinanceAdmin(admin.ModelAdmin):
    list_display = ('date_incurred', 'expense_type', 'amount_incurred')
    list_filter = ('expense_type', 'date_incurred')
    search_fields = ('expense_type',)
    ordering = ('date_incurred',)

admin.site.register(FarmFinance, FarmFinanceAdmin)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'employee_name', 'gender', 'phone_number', 'designation', 'date_hired')
    list_filter = ('gender', 'designation', 'date_hired')
    search_fields = ('employee_name', 'designation', 'phone_number')
    ordering = ('date_hired',)

admin.site.register(Employee, EmployeeAdmin)


class StockFeedAdmin(admin.ModelAdmin):
    list_display = ('feed_id', 'feed_type', 'quantity', 'unit_of_measurement', 'supplier_name', 'purchase_date', 'expiration_date', 'total_cost')
    list_filter = ('feed_type', 'supplier_name', 'purchase_date', 'expiration_date')
    search_fields = ('feed_type', 'supplier_name')
    ordering = ('purchase_date',)

admin.site.register(StockFeed, StockFeedAdmin)


