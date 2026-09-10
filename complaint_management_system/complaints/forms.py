# complaints/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Complaint

class StudentRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={"autocomplete": "given-name", "placeholder": "First name"}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={"autocomplete": "family-name", "placeholder": "Last name"}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "you@example.com"}))
    student_id = forms.CharField(max_length=30, required=True, label="Student ID", widget=forms.TextInput(attrs={"autocomplete": "off", "placeholder": "Your LTU student ID"}))
    program = forms.CharField(max_length=120, required=False, widget=forms.TextInput(attrs={"placeholder": "e.g. B.Tech in IT"}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel", "placeholder": "Phone number"}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "student_id", "program", "phone", "username", "password1", "password2"]

    def clean_student_id(self):
        sid = self.cleaned_data["student_id"]
        if Profile.objects.filter(student_id=sid).exists():
            raise forms.ValidationError("This Student ID is already registered.")
        return sid

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.create(
                user=user,
                student_id=self.cleaned_data["student_id"],
                program=self.cleaned_data.get("program", ""),
                phone=self.cleaned_data.get("phone", ""),
            )
        return user

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["category", "title", "description", "attachment"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Short, specific summary"}),
            "description": forms.Textarea(attrs={"rows": 6, "placeholder": "What happened, when, and where"}),
            "attachment": forms.ClearableFileInput(attrs={"accept": ".pdf,.png,.jpg,.jpeg,.doc,.docx"}),
        }

class ComplaintUpdateForm(forms.ModelForm):
    """Used by admins to change status and respond."""
    class Meta:
        model = Complaint
        fields = ["status", "admin_response"]
        widgets = {"admin_response": forms.Textarea(attrs={"rows": 4, "placeholder": "Add a clear update for the student"})}
