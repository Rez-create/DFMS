from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required  # Import for login requirement (optional)
from django.http import HttpResponseBadRequest
from decimal import Decimal
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from datetime import timedelta
import json
from core.models import MilkRecord, MilkSale, StockFeed, Animal, Breeding, FarmFinance, Employee


def index(request):
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)

    # -- Key metrics --
    total_animals = Animal.objects.count()
    total_cows = Animal.objects.filter(animal_type='Cow').count()
    total_calves = Animal.objects.filter(animal_type='Calf').count()
    total_employees = Employee.objects.count()

    # Milk production
    milk_records_30d = MilkRecord.objects.filter(milking_date__gte=thirty_days_ago)
    total_milk_30d = 0
    for r in milk_records_30d:
        total_milk_30d += (r.morning_milk_quantity or 0) + (r.afternoon_milk_quantity or 0) + (r.evening_milk_quantity or 0)

    milk_records_7d = MilkRecord.objects.filter(milking_date__gte=seven_days_ago)
    total_milk_7d = 0
    for r in milk_records_7d:
        total_milk_7d += (r.morning_milk_quantity or 0) + (r.afternoon_milk_quantity or 0) + (r.evening_milk_quantity or 0)

    # Revenue
    sales_30d = MilkSale.objects.filter(current_date__gte=thirty_days_ago)
    revenue_30d = Decimal('0.00')
    for sale in sales_30d:
        revenue_30d += sale.unit_price * Decimal(str(sale.amount_bought))

    sales_7d = MilkSale.objects.filter(current_date__gte=seven_days_ago)
    revenue_7d = Decimal('0.00')
    for sale in sales_7d:
        revenue_7d += sale.unit_price * Decimal(str(sale.amount_bought))

    # Expenses
    expenses_30d = FarmFinance.objects.filter(date_incurred__gte=thirty_days_ago).aggregate(
        total=Sum('amount_incurred')
    )['total'] or Decimal('0.00')

    # Expense breakdown by type (for pie chart)
    expense_breakdown = list(
        FarmFinance.objects.filter(date_incurred__gte=thirty_days_ago)
        .values('expense_type')
        .annotate(total=Sum('amount_incurred'))
        .order_by('-total')
    )
    expense_labels = json.dumps([e['expense_type'] for e in expense_breakdown])
    expense_values = json.dumps([float(e['total']) for e in expense_breakdown])

    # Monthly milk production (last 6 months for chart)
    six_months_ago = today - timedelta(days=180)
    monthly_milk_raw = (
        MilkRecord.objects.filter(milking_date__gte=six_months_ago)
        .annotate(month=TruncMonth('milking_date'))
        .values('month')
        .annotate(
            morning=Sum('morning_milk_quantity'),
            afternoon=Sum('afternoon_milk_quantity'),
            evening=Sum('evening_milk_quantity'),
        )
        .order_by('month')
    )
    milk_chart_labels = []
    milk_chart_data = []
    for entry in monthly_milk_raw:
        milk_chart_labels.append(entry['month'].strftime('%b %Y'))
        total = (entry['morning'] or 0) + (entry['afternoon'] or 0) + (entry['evening'] or 0)
        milk_chart_data.append(round(float(total), 1))
    milk_chart_labels = json.dumps(milk_chart_labels)
    milk_chart_data = json.dumps(milk_chart_data)

    # Monthly revenue (last 6 months for chart)
    monthly_revenue_raw = (
        MilkSale.objects.filter(current_date__gte=six_months_ago)
        .annotate(month=TruncMonth('current_date'))
        .values('month')
        .order_by('month')
    )
    revenue_chart_labels = []
    revenue_chart_data = []
    monthly_rev_agg = {}
    for sale in MilkSale.objects.filter(current_date__gte=six_months_ago):
        month_key = sale.current_date.replace(day=1)
        rev = sale.unit_price * Decimal(str(sale.amount_bought))
        monthly_rev_agg[month_key] = monthly_rev_agg.get(month_key, Decimal('0')) + rev
    for month_key in sorted(monthly_rev_agg.keys()):
        revenue_chart_labels.append(month_key.strftime('%b %Y'))
        revenue_chart_data.append(float(monthly_rev_agg[month_key]))
    revenue_chart_labels = json.dumps(revenue_chart_labels)
    revenue_chart_data = json.dumps(revenue_chart_data)

    # Upcoming calving
    upcoming_calving = Breeding.objects.filter(
        date_due_to_calve__gte=today,
        date_calved__isnull=True
    ).order_by('date_due_to_calve')[:5]

    # Recent sales
    recent_sales = MilkSale.objects.all().order_by('-current_date')[:5]

    # Recent expenses
    recent_expenses = FarmFinance.objects.all().order_by('-date_incurred')[:5]

    context = {
        'total_animals': total_animals,
        'total_cows': total_cows,
        'total_calves': total_calves,
        'total_employees': total_employees,
        'total_milk_30d': round(total_milk_30d, 1),
        'total_milk_7d': round(total_milk_7d, 1),
        'revenue_30d': revenue_30d,
        'revenue_7d': revenue_7d,
        'expenses_30d': expenses_30d,
        'profit_30d': revenue_30d - expenses_30d,
        'expense_labels': expense_labels,
        'expense_values': expense_values,
        'milk_chart_labels': milk_chart_labels,
        'milk_chart_data': milk_chart_data,
        'revenue_chart_labels': revenue_chart_labels,
        'revenue_chart_data': revenue_chart_data,
        'upcoming_calving': upcoming_calving,
        'recent_sales': recent_sales,
        'recent_expenses': recent_expenses,
    }
    return render(request, 'core/index.html', context)


# #######################################################################################
# ......................................................................................
# ///////////// ANIMAL RECORDS ///////////////////////////////////////////////////////////
def animal_records(request):
    if request.method == 'POST':
        animal_records = Animal(
            ear_tag=request.POST['ear_tag'],
            cow_name=request.POST['cow_name'],
            animal_type = request.POST.get('animal_types'),
            breed=request.POST['breed'],
            color=request.POST['color'],
            birth_date=request.POST['birth_date']
        )
        animal_records.save()
        return redirect('core:animal-records')  # Redirect to list view after creation
    else:
        # Display a form for creating a new animal
        animal_types = Animal.animal_types
        animals = Animal.objects.all()  # Fetch all animal objects
        context = {'animal_types': animal_types,
                   'animals': animals
                   }
        return render(request, 'core/animal_records.html', context)


def animal_list(request):
  animals = Animal.objects.all()  # Fetch all animal objects
  context = {'animals': animals}  # Create a dictionary for template context
  return render(request, 'core/animal_records.html', context)  # Render the template

def delete_animal_record(request, ear_tag):
    animal_record = Animal.objects.filter(ear_tag=ear_tag).first()
    
    if request.method == 'POST':
        animal_record.delete()
        return redirect('core:animal-records')  # Redirect to animal records page after deleting report
    
    return render(request, 'delete/animalrecord.html', {'animal_record': animal_record})


# #######################################################################################
# ......................................................................................
# ///////////// MILK RECORDS ///////////////////////////////////////////////////////////

def milk_records(request, record_id=None):
    if record_id:
        milk_record = MilkRecord.objects.filter(record_id=record_id).first()
    else:
        milk_record = None

    if request.method == 'POST':
        if milk_record is None:
            milk_record = MilkRecord(record_id=request.POST.get('record_id'))  # Set record_id for new records

        milking_date = request.POST.get('milking_date')
        cow_name = request.POST.get('cow_name')
        morning_milk_quantity = request.POST.get('morning_milk_quantity') or 0
        afternoon_milk_quantity = request.POST.get('afternoon_milk_quantity') or 0
        evening_milk_quantity = request.POST.get('evening_milk_quantity') or 0

        # Update the fields
        milk_record.milking_date = milking_date
        milk_record.cow_name = cow_name
        milk_record.morning_milk_quantity = float(morning_milk_quantity) 
        milk_record.afternoon_milk_quantity = float(afternoon_milk_quantity) 
        milk_record.evening_milk_quantity = float(evening_milk_quantity)

        # Save the record to the database
        milk_record.save()
        return redirect('core:milk-records')

    # Fetch all records for display
    milk_records = MilkRecord.objects.all().order_by('-milking_date')
    total_quantity = MilkRecord.total_milk_quantity
    context = {
        'milk_records': milk_records,
        'milk_record': milk_record,
        'total_quantity':total_quantity
    }
    return render(request, 'core/milk_records.html', context)

def delete_milk_record(request, record_id):
    milk_record = MilkRecord.objects.filter(record_id=record_id).first()
    
    if request.method == 'POST':
        milk_record.delete()
        return redirect('core:milk-records')  # Redirect to milk records page after deleting report
    
    return render(request, 'delete/milkrecord.html', {'milk_record': milk_record})


# #######################################################################################
# ......................................................................................
# ///////////// MILK SALE ///////////////////////////////////////////////////////////

def milk_sale(request):
    """Creates a new milk sale."""
    if request.method == 'POST':
        sale_id = request.POST.get('sale_id')
        current_date = request.POST.get('current_date')
        unit_price = request.POST.get('unit_price')
        client_name = request.POST.get('client_name')
        client_contact = request.POST.get('client_contact')
        amount_bought = request.POST.get('amount_bought')

        # Validate input data here (e.g., check if required fields are filled)

        try:
            unit_price = Decimal(unit_price)
            amount_bought = float(amount_bought)
        except (ValueError, TypeError):
            # Handle invalid input (e.g., show an error message)
            return render(request, 'milk_sale_create.html', {'error_message': 'Invalid input'})

        milk_sale = MilkSale(
            sale_id=sale_id,
            current_date=current_date,
            unit_price=unit_price,
            client_name=client_name,
            client_contact=client_contact,
            amount_bought=amount_bought
        )
        milk_sale.save()
        return redirect('core:milk-sale')  # Redirect to the dashboard after creation
    else:
        
        milk_sales = MilkSale.objects.all().order_by('-current_date')  # Order by most recent first
        total_price = MilkSale.total_milk_price
        context = {
            'milk_sales': milk_sales,
            'total_price': total_price
        }
        return render(request, 'core/milk_sale.html', context)
    
def delete_sale_record(request, sale_id):
    milk_sale = MilkSale.objects.filter(sale_id=sale_id).first()
    
    if request.method == 'POST':
        milk_sale.delete()
        return redirect('core:milk-sale')  # Redirect to milk sale page after deleting report
    
    return render(request, 'delete/milksale.html', {'milk_sale': milk_sale})



# #######################################################################################
# ......................................................................................
# ///////////// BREEDING INFO ///////////////////////////////////////////////////////////

def breeding(request, breeding_id=None):
    if breeding_id:
        breeding = Breeding.objects.filter(breeding_id=breeding_id).first()
    else:
        breeding = None

    if request.method == 'POST':
        if breeding is None:
            breeding = Breeding(
                breeding_id=request.POST.get('breeding_id')
            )
            
        breeding_id = request.POST.get('breeding_id')
        heat_date = request.POST.get('heat_date')
        breeding_date = request.POST.get('breeding_date')
        bull_name = request.POST.get('bull_name')
        cow_name = request.POST.get('cow_name')
        pregnancy_diagnosis_date = request.POST.get('pregnancy_diagnosis_date')
        date_due_to_calve = request.POST.get('date_due_to_calve')
        date_calved = request.POST.get('date_calved')
        age_of_cow_at_calving = request.POST.get('age_of_cow_at_calving')
        calf_name = request.POST.get('calf_name')
        calving_notes = request.POST.get('calving_notes')

        breeding.heat_date = heat_date
        breeding.breeding_date = breeding_date
        breeding.bull_name = bull_name
        breeding.cow_name = cow_name
        breeding.pregnancy_diagnosis_date = pregnancy_diagnosis_date
        breeding.date_due_to_calve = date_due_to_calve
        breeding.date_calved = date_calved
        breeding.age_of_cow_at_calving = age_of_cow_at_calving
        breeding.calf_name = calf_name
        breeding.calving_notes = calving_notes

        breeding.save()
        return redirect('core:breeding')

    breedings = Breeding.objects.all().order_by('-heat_date')  # Order by recent heat date
    context = {
        'breedings': breedings,
        'breeding': breeding
    }
    return render(request, 'core/breeding.html', context)

# List all breeding records
def breeding_list(request):
    breedings = Breeding.objects.all().order_by('-heat_date')  # Order by recent heat date
    context = {'breedings': breedings}
    return render(request, 'core/breeding.html', context)

# Delete a breeding record (consider confirmation or security measures)
def delete_breeding_record(request, breeding_id):
    breeding_record = Breeding.objects.filter(breeding_id=breeding_id).first()
    
    if request.method == 'POST':
        breeding_record.delete()
        return redirect('core:breeding')  # Redirect to animal records page after deleting report
    
    return render(request, 'delete/breedingdelete.html', {'breeding_record': breeding_record}) # Confirmation page

# Example view for searching breeding records (implement your search logic)
def breeding_search(request):
    query = request.GET.get('q')  # Get search query from URL parameters
    if query:
        # Implement your search logic here, filtering by relevant fields
        breedings = Breeding.objects.filter(heat_date__icontains=query)  # Example for heat date search
        context = {'breedings': breedings, 'query': query}
        return render(request, 'core/breeding.html', context)
    else:
        return HttpResponseBadRequest('Please provide a search query.')


# #######################################################################################
# ......................................................................................
# ///////////// STOCK FEEDS  ///////////////////////////////////////////////////////////


def stock_feeds(request):
    """
    Allows creation of a new stock feed entry.
    """
    if request.method == 'POST':
        def get_date_field(field_name): 
            field_value = request.POST.get(field_name) 
            return field_value if field_value else None
        
        stock_feeds = StockFeed(
            feed_id= request.POST.get('feed_id'),
            feed_type=request.POST['feed_types'],
            quantity=request.POST['quantity'],
            unit_of_measurement=request.POST['units'],
            supplier_name= request.POST['supplier_name'],
            supplier_contact=request.POST['supplier_contact'],
            supplier_phone=request.POST['supplier_phone'],
            purchase_date=request.POST['purchase_date'],
            expiration_date=request.POST['expiration_date'],
            cost_per_unit=request.POST['cost_per_unit'],
            notes=request.POST['notes']
        )
        stock_feeds.save()
        return redirect('core:stock-feeds')
    else:
        units = StockFeed.units
        feed_types = StockFeed.feed_types
        total_cost = StockFeed.total_feed_cost
        feeds = StockFeed.objects.all().order_by('-purchase_date')
        context = {
            'feeds': feeds,
            'units': units,
            'total_cost': total_cost,
            'feed_types': feed_types  # List of available feed types for dropdown menu in form
        }
        return render(request, 'core/stock_feeds.html', context)  # Replace with your template name

def delete_feed_record(request, feed_id):
    feed_record = StockFeed.objects.filter(feed_id=feed_id).first()
    
    if request.method == 'POST':
        feed_record.delete()
        return redirect('core:stock-feeds')  
    
    return render(request, 'delete/feeddelete.html', {'feed_record': feed_record})


# ########################### FARM FINANCE  #########################################
###################################################################################

def farm_finance(request):
    if request.method == 'POST':
        farm_finance = FarmFinance(
            date_incurred=request.POST.get('date_incurred'),
            expense_type=request.POST.get('expense_types'),
            amount_incurred=request.POST.get('amount_incurred')
        )
        farm_finance.save()
        return redirect('core:farm-finance')
    else:
        expense_types = FarmFinance.expense_types
        farm_finances = FarmFinance.objects.all().order_by('-date_incurred')
        context = {
            'farm_finances': farm_finances, 
            'expense_types': expense_types
        }
        return render(request, 'core/farm_finance.html', context)
      
def delete_finance_record(request, finance_id):
    finance_record = FarmFinance.objects.filter(finance_id=finance_id).first()
    
    if request.method == 'POST':
        finance_record.delete()
        return redirect('core:farm-finance')  
    
    return render(request, 'delete/financedelete.html', {'finance_record': finance_record})      
        
# ########################### EMPLOYEES   #########################################
###################################################################################
def employee(request):
    if request.method == 'POST':
        employee = Employee(
            employee_id=request.POST['employee_id'],
            employee_name=request.POST['employee_name'],
            gender=request.POST['gender'],
            phone_number=request.POST['phone_number'],
            address=request.POST['address'],
            designation=request.POST['designation_type'],
            date_hired=request.POST['date_hired'],
        )
        employee.save()
        return redirect('core:employee')
    else:
        designation_type = Employee.designation_type
        employees = Employee.objects.all().order_by('-date_hired')  # Get all farm finances from the database
        context = {
            'employees': employees,
            'designation_type': designation_type,  # Get all designation types from the database
        }
        return render(request, 'core/employees.html', context)

def delete_employee_record(request, employee_id):
    employee_record = Employee.objects.filter(employee_id=employee_id).first()
    
    if request.method == 'POST':
        employee_record.delete()
        return redirect('core:employee')  
    
    return render(request, 'delete/employeedelete.html', {'employee_record': employee_record})      
     