from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe
from Timesheets.models import User, ManualTimesheet, RegularTimesheet, JobCode

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "timesheet_display"]

    def timesheet_display(self, obj):
        reg = list(obj.regular_timesheet.all())
        man = list(obj.manual_timesheet.all())
        display_text = " ||| ".join(
            [
                "<a href={}>{} hours - {}</a>".format(
                    reverse(
                        f"admin:{timesheet._meta.app_label}_{timesheet._meta.model_name}_change",
                        args=(timesheet.pk,),
                    ),
                    round(timesheet.hours, 2),
                    "processed" if timesheet.espo_processed else "unprocessed",
                )
                for timesheet in reg + man
            ]
        )
        if display_text:
            return mark_safe(display_text)
        return "-"

    timesheet_display.short_description = "Timesheets"


@admin.register(ManualTimesheet)
class ManualTimesheetAdmin(admin.ModelAdmin):
    list_filter = ("espo_processed",)
    list_display = ("processed_display",)

    def processed_display(self, obj):
        return obj.espo_processed

    processed_display.short_description = "Espo Processed"


@admin.register(RegularTimesheet)
class RegularTimesheetAdmin(admin.ModelAdmin):
    list_filter = ("espo_processed", "user__last_name")
    list_display = ("id", "processed_display", "user_display")

    def processed_display(self, obj):
        return "Yes" if obj.espo_processed else "No"

    def user_display(self, obj):
        return mark_safe(
            "<a href={}>{} {}</a>".format(
                reverse(
                    f"admin:{obj.user._meta.app_label}_{obj.user._meta.model_name}_change",
                    args=(obj.user.pk,),
                ),
                obj.user.first_name,
                obj.user.last_name,
            )
        )

    processed_display.short_description = "Espo Processed"
    user_display.short_description = "User"


@admin.register(JobCode)
class JobCodeAdmin(admin.ModelAdmin):
    pass
