from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe
from Timesheets.models import User, ManualTimesheet, RegularTimesheet

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "timesheet_display"]

    def timesheet_display(self, obj):
        reg = list(obj.regular_timesheet.all())
        man = list(obj.manual_timesheet.all())
        display_text = ", ".join(
            [
                "<a href={}>{}</a>".format(
                    reverse(
                        "admin:{}_{}_change".format(
                            timesheet._meta.app_label, timesheet._meta.model_name
                        ),
                        args=(timesheet.pk,),
                    ),
                    timesheet.id,
                )
                for timesheet in reg + man
            ]
        )
        if display_text:
            return mark_safe(display_text)
        return "-"

    timesheet_display.short_description = "Link"


@admin.register(ManualTimesheet)
class ManualTimesheetAdmin(admin.ModelAdmin):
    pass


@admin.register(RegularTimesheet)
class RegularTimesheetAdmin(admin.ModelAdmin):
    pass
