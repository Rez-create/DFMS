from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from decimal import Decimal
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth
from datetime import timedelta
from django.core.paginator import Paginator
import json
from core.models import MilkRecord, MilkSale, StockFeed, Animal, Breeding, FarmFinance, Employee
from core.forms import AnimalForm, MilkRecordForm, MilkSaleForm, BreedingForm, StockFeedForm, FarmFinanceForm, EmployeeForm


@login_required
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
@login_required
def animal_records(request, ear_tag=None):
    # Handle edit
    animal = None
    if ear_tag:
        animal = get_object_or_404(Animal, ear_tag=ear_tag)
    
    if request.method == 'POST':
        form = AnimalForm(request.POST, instance=animal)
        if form.is_valid():
            form.save()
            return redirect('core:animal-records')
    else:
        form = AnimalForm(instance=animal)
    
    # Search and filter
    animals_list = Animal.objects.all().order_by('-birth_date')
    search_query = request.GET.get('search', '')
    animal_type_filter = request.GET.get('animal_type', '')
    
    if search_query:
        animals_list = animals_list.filter(
            Q(cow_name__icontains=search_query) |
            Q(ear_tag__icontains=search_query) |
            Q(breed__icontains=search_query)
        )
    
    if animal_type_filter:
        animals_list = animals_list.filter(animal_type=animal_type_filter)
    
    # Pagination
    paginator = Paginator(animals_list, 10)
    page_number = request.GET.get('page')
    animals = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'animals': animals,
        'animal': animal,
        'search_query': search_query,
        'animal_type_filter': animal_type_filter,
        'animal_types': Animal.animal_types
    }
    return render(request, 'core/animal_records.html', context)


def animal_list(request):
  animals = Animal.objects.all()  # Fetch all animal objects
  context = {'animals': animals}  # Create a dictionary for template context
  return render(request, 'core/animal_records.html', context)  # Render the template

@login_required
def delete_animal_record(request, ear_tag):
    animal_record = Animal.objects.filter(ear_tag=ear_tag).first()
    
    if request.method == 'POST':
        animal_record.delete()
        return redirect('core:animal-records')  # Redirect to animal records page after deleting report
    
    return render(request, 'delete/animalrecord.html', {'animal_record': animal_record})


# #######################################################################################
# ......................................................................................
# ///////////// MILK RECORDS ///////////////////////////////////////////////////////////

@login_required
def milk_records(request, record_id=None):
    milk_record = None
    if record_id:
        milk_record = get_object_or_404(MilkRecord, record_id=record_id)

    if request.method == 'POST':
        form = MilkRecordForm(request.POST, instance=milk_record)
        if form.is_valid():
            form.save()
            return redirect('core:milk-records')
    else:
        form = MilkRecordForm(instance=milk_record)

    # Search and filter
    milk_records_list = MilkRecord.objects.all().order_by('-milking_date')
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if search_query:
        milk_records_list = milk_records_list.filter(
            Q(cow_name__icontains=search_query) |
            Q(record_id__icontains=search_query)
        )
    
    if date_from:
        milk_records_list = milk_records_list.filter(milking_date__gte=date_from)
    if date_to:
        milk_records_list = milk_records_list.filter(milking_date__lte=date_to)
    
    # Pagination
    paginator = Paginator(milk_records_list, 10)
    page_number = request.GET.get('page')
    milk_records_page = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'milk_records': milk_records_page,
        'milk_record': milk_record,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to
    }
    return render(request, 'core/milk_records.html', context)

@login_required
def delete_milk_record(request, record_id):
    milk_record = MilkRecord.objects.filter(record_id=record_id).first()
    
    if request.method == 'POST':
        milk_record.delete()
        return redirect('core:milk-records')  # Redirect to milk records page after deleting report
    
    return render(request, 'delete/milkrecord.html', {'milk_record': milk_record})


# #######################################################################################
# ......................................................................................
# ///////////// MILK SALE ///////////////////////////////////////////////////////////

@login_required
def milk_sale(request, sale_id=None):
    milk_sale_obj = None
    if sale_id:
        milk_sale_obj = get_object_or_404(MilkSale, sale_id=sale_id)
    
    if request.method == 'POST':
        form = MilkSaleForm(request.POST, instance=milk_sale_obj)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.total_price = sale.unit_price * Decimal(str(sale.amount_bought))
            sale.save()
            return redirect('core:milk-sale')
    else:
        form = MilkSaleForm(instance=milk_sale_obj)
    
    # Search and filter
    milk_sales_list = MilkSale.objects.all().order_by('-current_date')
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if search_query:
        milk_sales_list = milk_sales_list.filter(
            Q(client_name__icontains=search_query) |
            Q(sale_id__icontains=search_query)
        )
    
    if date_from:
        milk_sales_list = milk_sales_list.filter(current_date__gte=date_from)
    if date_to:
        milk_sales_list = milk_sales_list.filter(current_date__lte=date_to)
    
    # Pagination
    paginator = Paginator(milk_sales_list, 10)
    page_number = request.GET.get('page')
    milk_sales = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'milk_sales': milk_sales,
        'milk_sale': milk_sale_obj,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to
    }
    return render(request, 'core/milk_sale.html', context)
    
@login_required
def delete_sale_record(request, sale_id):
    milk_sale = MilkSale.objects.filter(sale_id=sale_id).first()
    
    if request.method == 'POST':
        milk_sale.delete()
        return redirect('core:milk-sale')  # Redirect to milk sale page after deleting report
    
    return render(request, 'delete/milksale.html', {'milk_sale': milk_sale})



# #######################################################################################
# ......................................................................................
# ///////////// BREEDING INFO ///////////////////////////////////////////////////////////

@login_required
def breeding(request, breeding_id=None):
    breeding_obj = None
    if breeding_id:
        breeding_obj = get_object_or_404(Breeding, breeding_id=breeding_id)

    if request.method == 'POST':
        form = BreedingForm(request.POST, instance=breeding_obj)
        if form.is_valid():
            form.save()
            return redirect('core:breeding')
    else:
        form = BreedingForm(instance=breeding_obj)

    # Search and filter
    breedings_list = Breeding.objects.all().order_by('-breeding_date')
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if search_query:
        breedings_list = breedings_list.filter(
            Q(cow_name__icontains=search_query) |
            Q(bull_name__icontains=search_query) |
            Q(calf_name__icontains=search_query)
        )
    
    if date_from:
        breedings_list = breedings_list.filter(breeding_date__gte=date_from)
    if date_to:
        breedings_list = breedings_list.filter(breeding_date__lte=date_to)
    
    # Pagination
    paginator = Paginator(breedings_list, 10)
    page_number = request.GET.get('page')
    breedings = paginator.get_page(page_number)

    context = {
        'form': form,
        'breedings': breedings,
        'breeding': breeding_obj,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to
    }
    return render(request, 'core/breeding.html', context)

@login_required
def breeding_list(request):
    breedings = Breeding.objects.all().order_by('-heat_date')  # Order by recent heat date
    context = {'breedings': breedings}
    return render(request, 'core/breeding.html', context)

# Delete a breeding record (consider confirmation or security measures)
@login_required
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

@login_required
def stock_feeds(request, feed_id=None):
    feed = None
    if feed_id:
        feed = get_object_or_404(StockFeed, feed_id=feed_id)
    
    if request.method == 'POST':
        form = StockFeedForm(request.POST, instance=feed)
        if form.is_valid():
            stock_feed = form.save(commit=False)
            stock_feed.total_cost = stock_feed.quantity * stock_feed.cost_per_unit
            stock_feed.save()
            return redirect('core:stock-feeds')
    else:
        form = StockFeedForm(instance=feed)
    
    # Search and filter
    feeds_list = StockFeed.objects.all().order_by('-purchase_date')
    search_query = request.GET.get('search', '')
    feed_type_filter = request.GET.get('feed_type', '')
    
    if search_query:
        feeds_list = feeds_list.filter(
            Q(supplier_name__icontains=search_query) |
            Q(feed_id__icontains=search_query)
        )
    
    if feed_type_filter:
        feeds_list = feeds_list.filter(feed_type=feed_type_filter)
    
    # Pagination
    paginator = Paginator(feeds_list, 10)
    page_number = request.GET.get('page')
    feeds = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'feeds': feeds,
        'feed': feed,
        'search_query': search_query,
        'feed_type_filter': feed_type_filter,
        'feed_types': StockFeed.feed_types
    }
    return render(request, 'core/stock_feeds.html', context)

@login_required
def delete_feed_record(request, feed_id):
    feed_record = StockFeed.objects.filter(feed_id=feed_id).first()
    
    if request.method == 'POST':
        feed_record.delete()
        return redirect('core:stock-feeds')  
    
    return render(request, 'delete/feeddelete.html', {'feed_record': feed_record})


# ########################### FARM FINANCE  #########################################
###################################################################################

@login_required
def farm_finance(request, finance_id=None):
    finance = None
    if finance_id:
        finance = get_object_or_404(FarmFinance, finance_id=finance_id)
    
    if request.method == 'POST':
        form = FarmFinanceForm(request.POST, instance=finance)
        if form.is_valid():
            form.save()
            return redirect('core:farm-finance')
    else:
        form = FarmFinanceForm(instance=finance)
    
    # Search and filter
    farm_finances_list = FarmFinance.objects.all().order_by('-date_incurred')
    search_query = request.GET.get('search', '')
    expense_type_filter = request.GET.get('expense_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if search_query:
        farm_finances_list = farm_finances_list.filter(
            Q(finance_id__icontains=search_query)
        )
    
    if expense_type_filter:
        farm_finances_list = farm_finances_list.filter(expense_type=expense_type_filter)
    
    if date_from:
        farm_finances_list = farm_finances_list.filter(date_incurred__gte=date_from)
    if date_to:
        farm_finances_list = farm_finances_list.filter(date_incurred__lte=date_to)
    
    # Pagination
    paginator = Paginator(farm_finances_list, 10)
    page_number = request.GET.get('page')
    farm_finances = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'farm_finances': farm_finances,
        'finance': finance,
        'search_query': search_query,
        'expense_type_filter': expense_type_filter,
        'date_from': date_from,
        'date_to': date_to,
        'expense_types': FarmFinance.expense_types
    }
    return render(request, 'core/farm_finance.html', context)
      
@login_required
def delete_finance_record(request, finance_id):
    finance_record = FarmFinance.objects.filter(finance_id=finance_id).first()
    
    if request.method == 'POST':
        finance_record.delete()
        return redirect('core:farm-finance')  
    
    return render(request, 'delete/financedelete.html', {'finance_record': finance_record})      
        
# ########################### EMPLOYEES   #########################################
###################################################################################
@login_required
def employee(request, employee_id=None):
    emp = None
    if employee_id:
        emp = get_object_or_404(Employee, employee_id=employee_id)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=emp)
        if form.is_valid():
            form.save()
            return redirect('core:employee')
    else:
        form = EmployeeForm(instance=emp)
    
    # Search and filter
    employees_list = Employee.objects.all().order_by('-date_hired')
    search_query = request.GET.get('search', '')
    designation_filter = request.GET.get('designation', '')
    
    if search_query:
        employees_list = employees_list.filter(
            Q(employee_name__icontains=search_query) |
            Q(employee_id__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    if designation_filter:
        employees_list = employees_list.filter(designation=designation_filter)
    
    # Pagination
    paginator = Paginator(employees_list, 10)
    page_number = request.GET.get('page')
    employees = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'employees': employees,
        'employee': emp,
        'search_query': search_query,
        'designation_filter': designation_filter,
        'designation_type': Employee.designation_type
    }
    return render(request, 'core/employees.html', context)

@login_required
def delete_employee_record(request, employee_id):
    employee_record = Employee.objects.filter(employee_id=employee_id).first()
    
    if request.method == 'POST':
        employee_record.delete()
        return redirect('core:employee')  
    
    return render(request, 'delete/employeedelete.html', {'employee_record': employee_record})      
     