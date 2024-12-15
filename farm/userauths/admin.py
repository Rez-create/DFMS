from django.contrib import admin
from userauths.models import User

class UserAdmin(admin.ModelAdmin):
    search_fields = ['full_name', 'username']
    list_display = ['username', 'full_name', 'email', 'phone']



admin.site.register(User, UserAdmin)
