# DFMS - Dairy Farm Management System

A comprehensive web-based management system for dairy farms built with Django.

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

### Key Features
- ✅ User authentication (login/logout/register)
- ✅ Search and filter functionality across all modules
- ✅ Pagination for large datasets
- ✅ Form validation with Django Forms
- ✅ Edit and delete operations for all records
- ✅ Responsive dashboard with charts (ApexCharts)
- ✅ Date range filtering
- ✅ Protected routes with login_required

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
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

## Usage

### First Time Setup
1. Register a new account or login with superuser credentials
2. Add animals to the system
3. Record daily milk production
4. Track sales and expenses
5. Monitor breeding cycles

### Search & Filter
- Use the search bar to find records by name, ID, or other fields
- Apply filters by type, date range, or category
- Navigate through pages using pagination controls

### Edit Records
- Click the edit button on any record
- Modify the fields as needed
- Save changes


## Technologies Used

- **Backend**: Django 5.1.1
- **Database**: SQLite (development)
- **Frontend**: Bootstrap, ApexCharts
- **Admin**: Django Jazzmin
- **Authentication**: Django Auth

## Security Notes

⚠️ **Before deploying to production:**
1. Change `SECRET_KEY` in settings.py
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS`
4. Use environment variables for sensitive data
5. Switch to PostgreSQL or MySQL
6. Set up HTTPS
7. Configure proper backup strategy

## Support

For issues and questions, please open an issue on the repository.
