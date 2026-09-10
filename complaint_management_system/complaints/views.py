from django.shortcuts import render

# Create your views here.
# complaints/views.py
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from .forms import StudentRegisterForm, ComplaintForm, ComplaintUpdateForm
from .models import Complaint

staff_required = user_passes_test(lambda u: u.is_staff, login_url="dashboard")

def home(request):
    return render(request, "complaints/home.html")

def register(request):
    if request.method == "POST":
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. Welcome to LTU Complaint Portal.")
            return redirect("dashboard")
    else:
        form = StudentRegisterForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect("admin_complaint_list")
    complaints = request.user.complaints.select_related("category").all()
    return render(request, "complaints/student_dashboard.html", {"complaints": complaints})

@login_required
def complaint_create(request):
    if request.user.is_staff:
        return redirect("admin_complaint_list")
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = request.user
            complaint.save()
            messages.success(request, f"Complaint submitted — reference {complaint.reference}.")
            return redirect("complaint_detail", pk=complaint.pk)
    else:
        form = ComplaintForm()
    return render(request, "complaints/complaint_form.html", {"form": form})

@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint.objects.select_related("category", "student"), pk=pk)
    if not request.user.is_staff and complaint.student_id != request.user.id:
        messages.error(request, "You don't have access to that complaint.")
        return redirect("dashboard")

    if request.user.is_staff and request.method == "POST":
        form = ComplaintUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            messages.success(request, "Complaint updated.")
            return redirect("complaint_detail", pk=complaint.pk)
    else:
        form = ComplaintUpdateForm(instance=complaint) if request.user.is_staff else None

    return render(request, "complaints/complaint_detail.html", {"complaint": complaint, "form": form})

@staff_required
def admin_complaint_list(request):
    status = request.GET.get("status", "")
    complaints = Complaint.objects.select_related("category", "student").all()
    if status:
        complaints = complaints.filter(status=status)
    counts = {
        "all": Complaint.objects.count(),
        "PENDING": Complaint.objects.filter(status="PENDING").count(),
        "IN_PROGRESS": Complaint.objects.filter(status="IN_PROGRESS").count(),
        "RESOLVED": Complaint.objects.filter(status="RESOLVED").count(),
    }
    return render(
        request,
        "complaints/admin_dashboard.html",
        {"complaints": complaints, "active_status": status, "counts": counts},
    )