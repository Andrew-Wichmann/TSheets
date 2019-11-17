from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import mark_safe, format_html
from django.http.response import JsonResponse
from django.shortcuts import redirect
from Timesheets.models import (
    TSheetsUser,
    ManualTimesheet,
    RegularTimesheet,
    TimesheetEntry,
    TSheetsCompany,
)

# Register your models here.


@admin.register(TSheetsUser)
class TSheetsUserAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "timesheet_display"]

    def timesheet_display(self, obj):
        reg = list(obj.regular_timesheet.all())
        man = list(obj.manual_timesheet.all())
        display_text = " ||| ".join(
            [
                "<a href={}>{} hours</a>".format(
                    reverse(
                        f"admin:{timesheet._meta.app_label}_{timesheet._meta.model_name}_change",
                        args=(timesheet.pk,),
                    ),
                    round(timesheet.hours, 2),
                )
                for timesheet in reg + man
                if not timesheet.espo_processed
            ]
        )
        if display_text:
            return mark_safe(display_text)
        return "-"

    timesheet_display.short_description = "Unprocessed Timesheets"


class TimesheetAdmin(admin.ModelAdmin):
    list_filter = ("espo_processed", "user__last_name")
    list_display = ("id", "user_display", "hours_display", "espo_processed", "timesheet_group")

    def hours_display(self, obj):
        return round(obj.hours, 2)

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

    def timesheet_group(self, obj):
        timesheet_entry = obj.timesheet_entry
        return mark_safe(
            "<a href={}>Timesheet Entries (A week of timesheets)</a>".format(
                reverse(
                    f"admin:{timesheet_entry._meta.app_label}_{timesheet_entry._meta.model_name}_change",
                    args=(timesheet_entry.pk,),
                )
            )
        )

    user_display.short_description = "TSheetsUser"
    hours_display.short_description = "Hours"


@admin.register(ManualTimesheet)
class ManualTimesheetAdmin(TimesheetAdmin):
    pass


@admin.register(RegularTimesheet)
class RegularTimesheetAdmin(TimesheetAdmin):
    pass


@admin.register(TimesheetEntry)
class TimesheetEntry(admin.ModelAdmin):
    list_display = ("id", "user_display", "timesheet_actions", "weekendingdate")

    def user_display(self, obj):
        user = obj.user
        return mark_safe(
            "<a href={}>{} {}</a>".format(
                reverse(
                    f"admin:{user._meta.app_label}_{user._meta.model_name}_change", args=(user.pk,)
                ),
                user.first_name,
                user.last_name,
            )
        )

    def timesheet_actions(self, obj):
        if obj.processed:
            return "Processed!"
        else:
            return mark_safe(
                f'<a class="button" href="{reverse("admin:process_timesheet_entry", args=[obj.pk])}"/>Process<a>'
            )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:timesheet_entry_id>/process/",
                self.admin_site.admin_view(self.process),
                name="process_timesheet_entry",
            )
        ]
        return custom_urls + urls

    def process(self, request, timesheet_entry_id):
        timesheet_entry = self.get_object(request, timesheet_entry_id)
        if timesheet_entry.process():
            return redirect(request.META["HTTP_REFERER"])
        else:
            JsonResponse(
                {"timesheet_entry_id": timesheet_entry.id, "message": "Error processing timesheet"}
            )
