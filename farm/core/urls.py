from django.urls import path
from core import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    
    # animal view urls
    path("animal_records/", views.animal_records, name="animal-records"),
    path("animal_records/<str:ear_tag>/delete/", views.delete_animal_record, name='animal-records-delete'),
    
    # milk records view urls
    path("milk_records/", views.milk_records, name="milk-records"),
    path("milk_records/<str:record_id>/", views.milk_records, name='milk-records-edit'),
    path("milk_records/<str:record_id>/delete/", views.delete_milk_record, name='milk-records-delete'),
    
    # milk sale view urls
    path("milk_sale/", views.milk_sale, name="milk-sale"),
    path("milk_sale/<str:sale_id>/delete/", views.delete_sale_record, name='milk-sale-delete'),
    
    # breeding view urls
    path("breeding/", views.breeding, name="breeding"),
    path("breeding/<str:breeding_id>/", views.breeding, name='breeding-records-edit'),
    path('breeding/<str:breeding_id>/delete/', views.delete_breeding_record, name='breeding-records-delete'),
    
    # stock feeds view urls
    path("stock_feeds/", views.stock_feeds, name="stock-feeds"),
    path('stock_feeds/<str:feed_id>/delete/', views.delete_feed_record, name='feed-records-delete'),
    
    # farm finance view urls
    path("farm_finance/", views.farm_finance, name="farm-finance"),
    path('farm_finance/<str:finance_id>/delete/', views.delete_finance_record, name='finance-records-delete'),
    
    # employee view urls
    path("employee/", views.employee, name="employee"),
    path('employee/<str:employee_id>/delete/', views.delete_employee_record, name='employee-records-delete'),
]