from datetime import timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse, reverse_lazy
from .models import Book, Author, BorrowedBook, Penalty, Genre
from .forms import CustomUserCreationForm, AddBookForm, AddAuthorForm, AddGenreForm, BorrowedBookForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse

# Create your views here.

def home(request):
    search_term = request.GET.get('search','')
    book_list = []

    if search_term:
        book_list = Book.objects.filter(
            Q(title__icontains=search_term) |
            Q(isbn__icontains=search_term) |
            Q(authors__name__icontains=search_term) |
            Q(genres__name__icontains=search_term)
        ).distinct()

    return render(request, 'libraryApp/home.html', {'book_list': book_list})

class AddBookView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = AddBookForm
    template_name = 'libraryApp/add_book.html'
    success_url = reverse_lazy('add_book')  

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'librarian':
            raise PermissionDenied("You do not have permission to add books.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genre_form'] = AddGenreForm()
        context['author_form'] = AddAuthorForm()
        return context

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get('form_type')

        if form_type == 'genre_form':
            genre_form = AddGenreForm(request.POST)
            if genre_form.is_valid():
                genre_form.save()
        elif form_type == 'author_form':
            author_form = AddAuthorForm(request.POST)
            if author_form.is_valid():
                author_form.save()
        else:
            form = AddBookForm(request.POST)
            if form.is_valid():
                form.save()
        return HttpResponse(status=200)
    
        # return HttpResponse("Here's the text of the web page.")
        # return redirect(self.success_url)
    

# from django import forms
    
# class BookForm(forms.ModelForm):
#     genre_name = forms.CharField(max_length=100, required=False)
#     author_name = forms.CharField(max_length=100, required=False)

#     class Meta:
#         model = Book
#         fields = ['title', 'isbn','publication_year','available_copies','cover_image','genres','authors']

#     def save(self, commit=True):
#         # First, save the book instance
#         book = super().save(commit=False)

#         # Handle Genre
#         genre_name = self.cleaned_data.get('genre_name')
#         if genre_name:
#             genre, created = Genre.objects.get_or_create(name=genre_name)
#             book.genre = genre

#         # Handle Author
#         author_name = self.cleaned_data.get('author_name')
#         if author_name:
#             author, created = Author.objects.get_or_create(name=author_name)
#             book.author = author

#         if commit:
#             book.save()
#         return book

# def add_book_view(request):
#     if request.method == 'POST':
#         form = BookForm(request.POST)
#         if form.is_valid():
#             form.save()
#             # Redirect or provide success feedback
#     else:
#         form = BookForm()

#     context = {
#         'form': form,
#     }

    # return render(request, 'libraryApp/add_book1.html', context)

class BookListView(ListView):
    paginate_by = 3
    model = Book
    template_name = 'libraryApp/book_list.html'
    context_object_name = 'books_list'

class BookDetailView(DetailView):
    model = Book
    template_name = 'libraryApp/book_details.html'
   
class AuthorDetailView(DetailView):
    model = Author
    template_name = 'libraryApp/author_detail.html'

class BookUpdateView(UpdateView):
    model = Book
    form_class = AddBookForm
    template_name = 'libraryApp/add_book.html'
    def get_success_url(self):
        return reverse('book_detail', kwargs={'pk': self.object.pk})

def borrow_book_view(request, pk):
    book = get_object_or_404(Book, id=pk)
    user = request.user
    overdue_books = BorrowedBook.objects.filter(user=user, return_status=False, due_date__lte=timezone.now().date())  

    if request.method == 'POST':
        if overdue_books.exists():
            messages.error(request, "You have overdue books. Please return them before borrowing new books.")
            return redirect('book_detail', pk=book.id)
        
        borrowed_count = BorrowedBook.objects.filter(user=user, return_status=False).count()
        if borrowed_count >= 3:
            messages.error(request, "You can only borrow three books at a time.")
            return redirect('book_detail', pk=book.id)
        
        already_borrowed = BorrowedBook.objects.filter(user=user, book=book, return_status=False).exists()
        if already_borrowed:
            messages.error(request, "You have already borrowed this book.")
            return redirect('book_detail', pk=book.id)
        
        if book.available_copies > 0:
            BorrowedBook.objects.create(
                borrowed_date=timezone.now().date(),
                due_date=timezone.now().date() + timezone.timedelta(days=1),
                book=book,
                user=user
            )
            book.available_copies -= 1
            book.save()
            messages.success(request, "Book borrowed successfully!")
        else:
            messages.error(request, "No available copies of this book.")

        return redirect('book_detail', pk=book.id)

    return render(request, 'libraryApp/book_details.html', {
        'book': book,
        'overdue_books': overdue_books,
        'borrowed_count': borrowed_count,
        'already_borrowed': already_borrowed,
    })

def return_book_view(request, pk):
    borrowed_book = get_object_or_404(BorrowedBook, id=pk)
    book = borrowed_book.book
    
    if not borrowed_book.return_status:
        borrowed_book.return_date = timezone.now().date()
        borrowed_book.save()

        # Check if the book is overdue
        if borrowed_book.return_date > borrowed_book.due_date:
            overdue_days = (borrowed_book.return_date - borrowed_book.due_date).days
            penalty_amount = overdue_days * 1.00 
            penalty, created = Penalty.objects.get_or_create(
                borrowed_book=borrowed_book,
                defaults={'fine_amount': penalty_amount, 'payment_status': 'unpaid'}
            )
            if not created:
                # Only update the fine amount if the penalty is unpaid
                if penalty.payment_status == 'unpaid':
                    penalty.fine_amount = penalty_amount
                    penalty.save()
        else:
            penalty, created = Penalty.objects.get_or_create(
                borrowed_book=borrowed_book,
                defaults={'fine_amount': 0.00, 'payment_status': 'paid'}
            )
            if not created:
                penalty.fine_amount = 0.00
                penalty.payment_status = 'paid'
                penalty.save()

        penalty = Penalty.objects.filter(borrowed_book=borrowed_book).first()
        
        if penalty.payment_status != 'paid':
            messages.error(request, "You need to pay the penalty first!")
            return redirect('penalty_payment', pk=penalty.pk)
        else:
            borrowed_book.return_status = True
            borrowed_book.save()
            book.available_copies += 1
            book.save()
            messages.success(request, "Book returned successfully!")
            return redirect('activity_page')
    else:
        messages.error(request, "This book has already been returned.")
        return redirect('activity_page')

def penalty_payment_view(request, pk):
    penalty = get_object_or_404(Penalty, pk=pk)
    print(penalty.payment_status)
    if request.method == 'POST':
        penalty.payment_status = 'paid'
        penalty.payment_date = timezone.now().date()
        penalty.save()
        print(penalty.payment_status)
        messages.success(request, "Penalty paid successfully!")
        return redirect('activity_page')

    return render(request, 'libraryApp/penalty_payment.html', {'penalty': penalty})

def activity_page_view(request):
    user = request.user
    borrowed_books = BorrowedBook.objects.filter(user=user)
    paginator = Paginator(borrowed_books,7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'libraryApp/activity_page.html', {'page_obj':page_obj})


def library_activity_page(request):
    if request.user.role != 'librarian':
        raise PermissionDenied("You do not have permission to view library activity.")
    
    borrowed_books = BorrowedBook.objects.select_related('user', 'book', 'penalty').all()
    paginator = Paginator(borrowed_books,7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'libraryApp/library_activity.html', {'page_obj':page_obj})


def edit_borrowed_book(request, pk):
    borrowed_book = get_object_or_404(BorrowedBook, pk=pk)
    
    try:
        penalty = Penalty.objects.get(borrowed_book=borrowed_book)
    except Penalty.DoesNotExist:
        raise Http404("Penalty record does not exist for this borrowed book.")

    if request.method == 'POST':
        form = BorrowedBookForm(request.POST, instance=borrowed_book)
        if form.is_valid():
            form.save()
            # Update penalty status separately
            penalty_status = request.POST.get('penalty_status')
            penalty.payment_status = penalty_status
            penalty.save()
            return redirect('library_activity')
    else:
        form = BorrowedBookForm(instance=borrowed_book)

    return render(request, 'libraryApp/edit_borrowed_book.html', {
        'borrowed_book': borrowed_book,
        'penalty': penalty,
        'form': form
    })

@login_required
def delete_book(request,pk):
    if request.user.role != 'librarian':
        raise PermissionDenied("You do not have permission to delete books.")
    book = Book.objects.get(id=pk)
    if request.method=='POST':
        book.delete()
    return redirect('book-list')    

def signup_view(request):
    if request.method=="POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # messages.success(request, f"Welcome, Your account is created!!")
            return redirect('home')   
    else:
        form = CustomUserCreationForm()
    return render(request,'libraryApp/signup.html',{'form':form})

def login_view(request):
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            form = login(request, user)
            # messages.success(request, f' welcome {username} !!')
            return redirect('home')
        else:
            messages.info(request, f'account does not exist please Sign up')
    form = AuthenticationForm() #empty form
    return render(request, 'libraryApp/login.html',{'form':form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    user = request.user
    return render(request, 'libraryApp/profile.html', {'user':user})
