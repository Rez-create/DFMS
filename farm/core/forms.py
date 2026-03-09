from django import forms
from core.models import Animal, MilkRecord, MilkSale, Breeding, StockFeed, FarmFinance, Employee
from django.core.exceptions import ValidationError
from datetime import date

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = '__all__'
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > date.today():
            raise ValidationError("Birth date cannot be in the future.")
        return birth_date

class MilkRecordForm(forms.ModelForm):
    class Meta:
        model = MilkRecord
        fields = '__all__'
        widgets = {
            'milking_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        morning = cleaned_data.get('morning_milk_quantity') or 0
        afternoon = cleaned_data.get('afternoon_milk_quantity') or 0
        evening = cleaned_data.get('evening_milk_quantity') or 0
        
        if morning < 0 or afternoon < 0 or evening < 0:
            raise ValidationError("Milk quantities cannot be negative.")
        return cleaned_data

class MilkSaleForm(forms.ModelForm):
    class Meta:
        model = MilkSale
        fields = '__all__'
        widgets = {
            'current_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_amount_bought(self):
        amount = self.cleaned_data.get('amount_bought')
        if amount and amount <= 0:
            raise ValidationError("Amount must be greater than zero.")
        return amount
    
    def clean_unit_price(self):
        price = self.cleaned_data.get('unit_price')
        if price and price <= 0:
            raise ValidationError("Price must be greater than zero.")
        return price

class BreedingForm(forms.ModelForm):
    class Meta:
        model = Breeding
        fields = '__all__'
        widgets = {
            'heat_date': forms.DateInput(attrs={'type': 'date'}),
            'breeding_date': forms.DateInput(attrs={'type': 'date'}),
            'pregnancy_diagnosis_date': forms.DateInput(attrs={'type': 'date'}),
            'date_due_to_calve': forms.DateInput(attrs={'type': 'date'}),
            'date_calved': forms.DateInput(attrs={'type': 'date'}),
        }

class StockFeedForm(forms.ModelForm):
    class Meta:
        model = StockFeed
        fields = '__all__'
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        return quantity

class FarmFinanceForm(forms.ModelForm):
    class Meta:
        model = FarmFinance
        fields = '__all__'
        widgets = {
            'date_incurred': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_amount_incurred(self):
        amount = self.cleaned_data.get('amount_incurred')
        if amount and amount <= 0:
            raise ValidationError("Amount must be greater than zero.")
        return amount

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'
        widgets = {
            'date_hired': forms.DateInput(attrs={'type': 'date'}),
        }
