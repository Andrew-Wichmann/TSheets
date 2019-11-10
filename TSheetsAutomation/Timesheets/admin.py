from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import mark_safe, format_html
from django.http.response import JsonResponse
from django.shortcuts import redirect
from Timesheets.models import (
    TSheetsUser,
    ManualTimesheet,
    RegularTimesheet,
    JobCode,
    TSheetsCompany,
)

# Register your models here.


@admin.register(TSheetsCompany)
class TSheetsCompanyAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(TSheetsUser)
class TSheetsUserAdmin(admin.ModelAdmin):
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


class TimesheetAdmin(admin.ModelAdmin):
    list_filter = ("espo_processed", "user__last_name")
    list_display = ("id", "user_display", "hours_display", "espo_processed", "timesheet_actions")

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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:timesheet_id>/process/",
                self.admin_site.admin_view(self.process),
                name="process_timesheet",
            )
        ]
        return custom_urls + urls

    def process(self, request, timesheet_id):
        timesheet = self.get_object(request, timesheet_id)
        if timesheet.process():
            return redirect(request.META["HTTP_REFERER"])
        else:
            JsonResponse({"timesheet_id": timesheet.id, "message": "Error processing timesheet"})

    def timesheet_actions(self, obj):
        if obj.espo_processed:
            return "None"
        else:
            return mark_safe(
                f'<a class="button" href="{reverse("admin:process_timesheet", args=[obj.pk])}"/>Process<a>'
            )

    user_display.short_description = "TSheetsUser"
    hours_display.short_description = "Hours"


@admin.register(ManualTimesheet)
class ManualTimesheetAdmin(TimesheetAdmin):
    pass


@admin.register(RegularTimesheet)
class RegularTimesheetAdmin(TimesheetAdmin):
    pass


@admin.register(JobCode)
class JobCodeAdmin(admin.ModelAdmin):
    pass
