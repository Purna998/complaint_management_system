from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.urls import reverse


class Profile(models.Model):
    """Extra fields for a student account. Admins (is_staff=True) don't
    need one of these — they just use the regular User fields."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    student_id = models.CharField(max_length=30, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    program = models.CharField(max_length=120, blank=True, help_text="e.g. B.Tech in IT")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.student_id})"


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Complaint(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        RESOLVED = "RESOLVED", "Resolved"

    reference = models.CharField(max_length=12, unique=True, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="complaints"
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="complaints")
    title = models.CharField(max_length=150)
    description = models.TextField()
    attachment = models.FileField(upload_to="complaint_attachments/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} — {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            last = Complaint.objects.order_by("id").last()
            next_id = (last.id + 1) if last else 1
            self.reference = f"LTU-{next_id:06d}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("complaint_detail", args=[self.pk])