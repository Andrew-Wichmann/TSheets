from django.contrib import admin
from jobdiva.models import Candidate, Company, Job, Hire
from django.urls import reverse
from django.utils.html import mark_safe

# Register your models here.


@admin.register(Hire)
class HireAdmin(admin.ModelAdmin):
    list_display = ["ACTIVITYID", "first_name", "last_name", "email"]

    def first_name(self, obj):
        return obj.CANDIDATE.FIRSTNAME

    def last_name(self, obj):
        return obj.CANDIDATE.LASTNAME

    def email(self, obj):
        return obj.CANDIDATE.EMAIL


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    pass


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    pass


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):

    list_display = ["ID", "FIRSTNAME", "LASTNAME", "tsheets_user_display"]

    def tsheets_user_display(self, obj):
        user = obj.tsheets_user
        display_text = "<a href={}>{}</a>".format(
            reverse(
                f"admin:{user._meta.app_label}_{user._meta.model_name}_change",
                args=(user.pk,),
            )
        )

        if display_text:
            return mark_safe(display_text)
        return "-"
