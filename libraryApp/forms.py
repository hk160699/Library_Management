from datetime import datetime
from django import forms
from .models import CustomUser, Book, Genre, Author, BorrowedBook
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=64)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    class Meta:
        model = CustomUser
        fields = ['username', 'email','password1', 'password2', 'role', 'mobile_number', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class AddBookForm(forms.ModelForm):
    authors = forms.ModelMultipleChoiceField(queryset=Author.objects.all(),
        widget=FilteredSelectMultiple('Authors', is_stacked=False), required=True
    )
    genres = forms.ModelMultipleChoiceField(queryset=Genre.objects.all(),
        widget=FilteredSelectMultiple('Genres', is_stacked=False), required=True
    )
    class Meta:
        model = Book
        fields = ['title', 'isbn','publication_year','available_copies','cover_image','genres','authors']
    class Media:
        css = {'all': ('/static/admin/css/widgets.css',), }
        js = ('/admin/jsi18n'),
    
    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if not isbn.isdigit():
            raise ValidationError("The ISBN Number should contain only digits.")
        return isbn
    
    def clean_publication_year(self):
        publication_year=self.cleaned_data.get('publication_year')
        current_year=datetime.now().year
        if not 1000<=publication_year<=current_year : 
            raise ValidationError("The Publication Year should be valid year.")
        return publication_year
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     genres = cleaned_data.get('genres')
    #     authors = cleaned_data.get('authors')
        
    #     if not genres:
    #         self.add_error('genres', 'At least one genre must be selected.')
        
    #     if not authors:
    #         self.add_error('authors', 'At least one author must be selected.')
        
    #     return cleaned_data

class AddAuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name','date_of_birth','nationality']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class AddGenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name']

class BorrowedBookForm(forms.ModelForm):
    class Meta:
        model = BorrowedBook
        fields = ['due_date', 'return_date', 'return_status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'return_date': forms.DateInput(attrs={'type': 'date'}),
            'return_status': forms.Select(choices=[('Not Returned', 'Not Returned'), ('Returned', 'Returned')]),
        }

