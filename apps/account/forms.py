from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

from apps.dashboard.models import Company

CustomUser = get_user_model()


class StudentRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        UserCreationForm.__init__(self, *args, **kwargs)
        self.fields['gender'].required = True
        self.fields['first_name'].label = "First Name :"
        self.fields['last_name'].label = "Last Name :"
        self.fields['password1'].label = "Password :"
        self.fields['password2'].label = "Confirm Password :"
        self.fields['email'].label = "Email :"
        self.fields['gender'].label = "Gender :"

        self.fields['first_name'].widget.attrs.update(
            {
                'placeholder': 'Enter First Name',
            }
        )
        self.fields['last_name'].widget.attrs.update(
            {
                'placeholder': 'Enter Last Name',
            }
        )
        self.fields['email'].widget.attrs.update(
            {
                'placeholder': 'Enter Email',
            }
        )
        self.fields['password1'].widget.attrs.update(
            {
                'placeholder': 'Enter Password',
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'placeholder': 'Confirm Password',
            }
        )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', 'gender']

    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        if not gender:
            raise forms.ValidationError("Gender is required")
        return gender

    def save(self, commit=True):
        user = UserCreationForm.save(self, commit=False)
        user.role = 2
        if commit:
            user.save()
        return user


class EnterpriseRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        UserCreationForm.__init__(self, *args, **kwargs)
        self.fields['gender'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        # self.fields['first_name'].label = "Company Name"
        # self.fields['last_name'].label = "Company Address"
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm Password"

        # self.fields['first_name'].widget.attrs.update(
        #     {
        #         'placeholder': 'Enter Company Name',
        #     }
        # )
        # self.fields['last_name'].widget.attrs.update(
        #     {
        #         'placeholder': 'Enter Company Address',
        #     }
        # )
        self.fields['email'].widget.attrs.update(
            {
                'placeholder': 'Enter Email',
            }
        )
        self.fields['password1'].widget.attrs.update(
            {
                'placeholder': 'Enter Password',
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'placeholder': 'Confirm Password',
            }
        )
    class Meta:
        model=CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2', "gender"]


    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        if not gender:
            raise forms.ValidationError("Gender is required")
        return gender


    def save(self, commit=True):
        user = UserCreationForm.save(self,commit=False)
        user.role = 3
        if commit:
            user.save()
        return user


class CompanyRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['phone'].required = True
        self.fields['website'].required = True
        self.fields['name'].label = "Company Name"
        self.fields['description'].label = "Short company description"
        # self.fields['password1'].label = "Password"
        # self.fields['password2'].label = "Confirm Password"

        self.fields['name'].widget.attrs.update(
            {
                'placeholder': 'Enter Company Name',
            }
        )
        # self.fields['last_name'].widget.attrs.update(
        #     {
        #         'placeholder': 'Enter Company Address',
        #     }
        # )
        # self.fields['email'].widget.attrs.update(
        #     {
        #         'placeholder': 'Enter Email',
        #     }
        # )
        # self.fields['password1'].widget.attrs.update(
        #     {
        #         'placeholder': 'Enter Password',
        #     }
        # )
        # self.fields['password2'].widget.attrs.update(
        #     {
        #         'placeholder': 'Confirm Password',
        #     }
        # )
    class Meta:
        model=Company
        fields = ['name', 'description', 'phone', 'website']



class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "autocomplete": "email",
                "class": "form-control",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "autocomplete": "current-password",
                "class": "form-control",
            }
        )
    )