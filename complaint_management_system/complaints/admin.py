from django.contrib import admin

# Register your models here.
# complaints/admin.py
from django.contrib import admin
from .models import Profile, Category, Complaint

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "student_id", "program", "phone")
    search_fields = ("student_id", "user__username", "user__first_name", "user__last_name")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("reference", "title", "student", "category", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("reference", "title", "student__username")