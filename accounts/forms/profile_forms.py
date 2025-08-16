from django import forms
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.models import User


class UserProfileForm(BaseUserChangeForm):
    """Custom form for user profile updates."""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-background-primary border border-border-primary rounded-lg text-foreground-primary placeholder-foreground-tertiary focus:ring-2 focus:ring-brand-primary focus:border-brand-primary transition-colors',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-background-primary border border-border-primary rounded-lg text-foreground-primary placeholder-foreground-tertiary focus:ring-2 focus:ring-brand-primary focus:border-brand-primary transition-colors',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 bg-background-primary border border-border-primary rounded-lg text-foreground-primary placeholder-foreground-tertiary focus:ring-2 focus:ring-brand-primary focus:border-brand-primary transition-colors',
                'placeholder': 'Enter your email address'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password field from the form
        if 'password' in self.fields:
            del self.fields['password']
        
        # Update field labels
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['email'].label = 'Email Address'
        
        # Make email required
        self.fields['email'].required = True
