from django import forms
from django.contrib.auth.models import User

from main.models import Member, Deposit

GENDER_CHOICES = {"Male": "Male", "Female": "Female"}
class MemberForm(forms.ModelForm):
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect)
    class Meta:
        model = Member
        fields = ['first_name', 'last_name', 'email', 'dob', 'department', 'gender', 'profile_pic']
        widgets = {
            'dob' : forms.DateInput(attrs={'type': 'date', 'min':'1980-01-01', 'max':'2005-12-31'}),
            'weight': forms.NumberInput(attrs={'type': 'number', 'min':'35', 'max':'100'})
        }


class DepositForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'type': 'number', 'min':'0', 'max':'100000'})
        }

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)


class MemberRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Member
        fields = ['username', 'first_name', 'last_name', 'email', 'dob', 'gender', 'profile_pic']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        member = super().save(commit=False)
        member.user = user
        if commit:
            member.save()
        return member


# Update Customer/ Gender radio button
# Cloning and setting up the virtual env