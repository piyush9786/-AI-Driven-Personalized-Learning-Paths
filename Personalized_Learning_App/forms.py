from django import forms
from .models import StudyRoom
from django.contrib.auth.models import User

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered.")
        
        return cleaned_data
    

class StudyRoomForm(forms.ModelForm):
    class Meta:
        model = StudyRoom
        fields = ['name', 'course_name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }