
from django.contrib import admin

from main.models import Member, Deposit, Department

# Register your models here.
admin.site.site_header = "ACK ST Andrews'"
admin.site.site_title = 'Church Admin'

class MemberAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'gender', 'dob']
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ['gender']
    list_per_page = 25

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'head']
    search_fields = ['name', 'description', 'head']
    list_filter = ['name']
    list_per_page = 25

class DepositAdmin(admin.ModelAdmin):
    list_display = ['member', 'created_at', 'status', 'amount']
    search_fields = ['member__first_name', 'status', 'amount']
    list_per_page = 25
    list_filter = ['status']

admin.site.register(Member, MemberAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(Department, DepartmentAdmin)



# python manage.py --help

# python manage.py createsuperuser
# admin@gmail.com
# 123456

# localhost:8000/admin