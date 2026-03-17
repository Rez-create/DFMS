# DFMS - Dairy Farm Management System

A comprehensive web-based management system for dairy farms.

## Features

### Core Modules
- **Dashboard**: Real-time KPIs, charts, and analytics
- **Animal Records**: Manage cows and calves with complete tracking
- **Milk Records**: Track daily milk production (morning, afternoon, evening)
- **Milk Sales**: Record and manage milk sales to clients
- **Breeding**: Track breeding cycles, pregnancy, and calving
- **Stock Feeds**: Inventory management for animal feeds
- **Farm Finance**: Expense tracking and financial management
- **Employee Management**: Staff records and management


### Setup


```bash
cd DFMS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Navigate to the farm directory:
```bash
cd farm
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application at `http://127.0.0.1:8000/`


## Technologies Used

- **Backend**: Django 5.1.1
- **Database**: PostgreSQL
- **Frontend**: Bootstrap, ApexCharts
- **Admin**: Django Jazzmin
- **Authentication**: Django Auth

