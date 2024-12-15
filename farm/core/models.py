from django.db import models
from django.utils import timezone
from shortuuid.django_fields import ShortUUIDField
from datetime import timedelta 
from decimal import Decimal
from datetime import date


class MilkRecord(models.Model):
    record_id = ShortUUIDField(unique=True, primary_key=True, length=3, max_length=20, prefix="R", alphabet="123456789")
    milking_date = models.DateField(default=timezone.now)  # Date of milking
    cow_name = models.CharField(max_length=255, default='Unknown')  # Name of the cow
    morning_milk_quantity = models.FloatField(blank=True, null=True)  # Quantity of milk in the morning
    afternoon_milk_quantity = models.FloatField(blank=True, null=True, default='0')  # Quantity of milk in the afternoon
    evening_milk_quantity = models.FloatField(blank=True, null=True, default='0') # Quantity of milk in the evening

    def total_milk_quantity(self):
        """Calculate the total milk quantity for the day."""
        return self.morning_milk_quantity + self.afternoon_milk_quantity + self.evening_milk_quantity

    def __str__(self):
        return f"Milk Record for {self.cow_name} on {self.milking_date}"
 
 
 
class MilkSale(models.Model):
    sale_id = ShortUUIDField(unique=True, primary_key=True, length=3, max_length=20, prefix="S", alphabet="123456789")
    current_date = models.DateField()  # Automatically set the date when the sale is created
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per litre
    client_name = models.CharField(max_length=100)  # Name of the client
    client_contact = models.CharField(max_length=15)  # Contact information of the client
    amount_bought = models.FloatField()  # Amount of milk bought in litres
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Total price for the sale

    def total_milk_price(self):
        """Override save method to calculate total price before saving."""
        # Convert amount_bought_in_litres to Decimal for the calculation
        amount_in_decimal = Decimal(self.amount_bought)
        self.total_price = self.unit_price * amount_in_decimal
        return self.total_price

    def __str__(self):
        return f"Sale of {self.amount_bought} litres to {self.client_name} on {self.current_date}"
    
       
    
class Animal(models.Model):
    animal_types = [
        ('Cow', 'Cow'),
        ('Calf', 'Calf'),
    ]
    
    ear_tag = ShortUUIDField(unique=True, primary_key=True, length=3, max_length=20, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZO123456789")
    cow_name = models.CharField(max_length=100)
    animal_type = models.CharField(max_length=10, default="Cow", choices=animal_types)
    breed = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    birth_date = models.DateField()

    def age(self): 
        today = date.today() 
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day)) 
        return age

    def __str__(self):
        return self.cow_name
    

class Breeding(models.Model):
    breeding_id = ShortUUIDField(unique=True, primary_key=True, length=3, max_length=20, prefix="B", alphabet="0123456789")
    heat_date = models.DateField(null=True, blank=True)  # Date when the cow was in heat
    breeding_date = models.DateField()  # Date when breeding occurred
    bull_name = models.CharField(max_length=100)  # Name of the bull
    cow_name = models.CharField(max_length=100)  # Name of the cow
    pregnancy_diagnosis_date = models.DateField(null=True, blank=True)  # Date when pregnancy was diagnosed
    date_due_to_calve = models.DateField(null=True, blank=True)  # Expected due date for calving
    date_calved = models.DateField(null=True, blank=True)  # Actual calving date
    age_of_cow_at_calving = models.PositiveIntegerField(null=True, blank=True)  # Age of the cow at the time of calving (in years)
    calf_name = models.CharField(max_length=100, null=True, blank=True)  # Name of the calf
    calving_notes = models.TextField(blank=True, null=True)  # Additional notes regarding the calving process

    def __str__(self):
        return f"Breeding record for {self.cow_name} with {self.bull_name} on {self.breeding_date}"



class FarmFinance(models.Model):
    expense_types = [
        ('Feed', 'Feed'),
        ('Veterinary', 'Veterinary'),
        ('Equipment', 'Equipment'),
        ('Labor', 'Labor'),
        ('Maintenance', 'Maintenance'),
        ('Other', 'Other'),
    ] 

    finance_id = ShortUUIDField(unique=True, primary_key=True, length=3, max_length=20, prefix="F", alphabet="0123456789")
    date_incurred = models.DateField(default=timezone.now)
    expense_type = models.CharField(max_length=20, choices=expense_types, null=True, default='Other')
    amount_incurred = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.expense_type} on {self.date_incurred}: ${self.amount_incurred}"


class Employee(models.Model):
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
    ]
    
    designation_type = [
        ('Farm Manager', 'Farm Manager'),
        ('Milker', 'Milker'),
        ('Herdsman', 'Herdsman'),
    ] 

    employee_id = models.CharField(max_length=10, primary_key=True)  # Automatically incrementing ID
    employee_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)  # Adjust length based on expected format
    address = models.TextField()
    designation = models.CharField(max_length=20, choices=designation_type, null=True, default='Milker')
    date_hired = models.DateField()

    def __str__(self):
        return f"{self.employee_name} ({self.designation})"
    


class StockFeed(models.Model):
    feed_types = [
        ('Hay', 'Hay'),
        ('Silage', 'Silage'),
        ('Nappier', 'Nappier'),
        ('Dairy Meal', 'Dairy Meal'),
        ('Maize Brand', 'Maize Brand'),
        ('Salt suppliment', 'Salt suppliment'),
        # Add more feed types as needed
    ]
    
    units = [
        ('Kilogram(kg)', 'Kilogram(kg)'),
        ('gram(g)', 'gram(g)'),
        ('Litres(l)', 'Litres(l)'),
        # Add more units as needed
    ]
    feed_id = ShortUUIDField(unique=True, primary_key=True, length=3, max_length=20, prefix="F", alphabet="123456789")
    feed_type = models.CharField(max_length=50, choices=feed_types)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_of_measurement = models.CharField(max_length=15, choices=units)  # e.g., kg, g
    supplier_name = models.CharField(max_length=100)  # Supplier name
    supplier_contact = models.CharField(max_length=100, blank=True, null=True)  # Contact person
    supplier_phone = models.CharField(max_length=15, blank=True, null=True)  # Supplier phone number
    purchase_date = models.DateField()
    expiration_date = models.DateField(blank=True, null=True)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=0, default=Decimal('0.00'))

    def total_feed_cost(self):
        """Calculate the total cost of feeds for the day."""
        self.total_cost = self.quantity * self.cost_per_unit
        return self.total_cost

    def __str__(self):
        return f"{self.feed_type} - {self.quantity} {self.unit_of_measurement}"

 
    
  