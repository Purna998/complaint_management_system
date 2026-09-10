from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Complaint, Profile


class PortalPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(
            username="student", password="test-password", first_name="Asha"
        )
        Profile.objects.create(user=cls.student, student_id="LTU-TEST-1")
        cls.staff = User.objects.create_user(
            username="staff", password="test-password", is_staff=True
        )
        cls.category = Category.objects.create(name="Academic")
        cls.complaint = Complaint.objects.create(
            student=cls.student,
            category=cls.category,
            title="Test complaint",
            description="A test submission.",
        )

    def test_public_pages_render_with_portal_branding(self):
        for url_name in ("home", "login", "register"):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Lumbini Technological University")
                self.assertContains(response, "css/theme.css")

    def test_student_dashboard_and_detail_render(self):
        self.client.force_login(self.student)
        dashboard = self.client.get(reverse("dashboard"))
        detail = self.client.get(reverse("complaint_detail", args=[self.complaint.pk]))
        self.assertContains(dashboard, self.complaint.reference)
        self.assertContains(detail, self.complaint.title)
        self.assertNotContains(dashboard, "â")

    def test_staff_dashboard_filters_complaints(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("admin_complaint_list"), {"status": "PENDING"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.complaint.reference)
        self.assertContains(response, "Complaint overview")

    def test_logout_uses_post(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)
