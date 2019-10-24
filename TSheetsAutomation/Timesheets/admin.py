from django.contrib import admin
from Timesheets.models import Owner, Timesheet

# Register your models here.


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    pass


@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    pass
