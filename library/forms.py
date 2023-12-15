from django import forms
from django.forms import ModelForm,TextInput,EmailInput,DateInput,DateField
from .models import Members,Book,Transactions

class MemberForm(forms.Form):
    first_name=forms.CharField(label="First Name",max_length=100)
    last_name=forms.CharField(label="Last Name", max_length=100)
    email=forms.EmailField()

class AddBookForm(forms.Form):
    title=forms.CharField(label="Title",max_length=100,required=False)
    authors=forms.CharField(label="Authors",max_length=100,required=False)
    isbn=forms.CharField(label="isbn",max_length=100,required=False)
    publisher=forms.CharField(label="publisher",max_length=100,required=False)
    page=forms.CharField(label="Pages",max_length=50,required=False)
    quantity=forms.IntegerField(label="Quantity", min_value=1,required=False)

class BookIssueForm(ModelForm):
    class Meta:
        model=Transactions
        fields = [
            'book',
            'member',
            'issue_date',
        ]

        widgets = {
            'issue_date': forms.DateInput(
                attrs={
                    'type': 'date', 
                    'placeholder': 'yyyy-mm-dd (DOB)', 
                    'class': 'form-control',
                    'style': 'max-width:300px',
                }
            ),

            'book': forms.Select(
                attrs={
                    'style': 'max-width:300px',
                }
            ),
            'member': forms.Select(
                attrs={
                    'style': 'max-width:300px',
                }
            ),
        }

class BookReturnForm(ModelForm):
    class Meta:
        model=Transactions
        fields = [
            'book',
            'member',
            'return_date',
        ]

        widgets = {
            'return_date': forms.DateInput(
                attrs={
                    'type': 'date', 
                    'placeholder': 'yyyy-mm-dd (DOB)', 
                    'class': 'form-control',
                    'style': 'max-width:300px',
                }
            ),

            'book': forms.Select(
                attrs={
                    'style': 'max-width:300px',
                }
            ),
            'member': forms.Select(
                attrs={
                    'style': 'max-width:300px',
                }
            ),
        }
    