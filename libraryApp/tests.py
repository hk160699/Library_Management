from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from libraryApp.models import Book, Penalty
import pytest
from django.contrib.messages import get_messages
from .fixtures import create_user,  create_librarian, create_book, create_genre, create_author
from libraryApp.models import  Book, BorrowedBook

@pytest.mark.django_db
def test_add_book_view_librarian(client, create_librarian, create_genre, create_author):
    librarian = create_librarian
    client.login(username=librarian.username, password='password456')
    response = client.post(reverse('add_book'), {
        'title': 'Sample Book',
        'isbn': '2345678',
        'publication_year': 2001,
        'available_copies': 10,
        'cover_image': '',
        'genres': [create_genre.id],
        'authors': [create_author.id]
    })
    assert response.status_code == 302
    assert Book.objects.filter(title='Sample Book').exists()

@pytest.mark.django_db
def test_add_book_view_non_librarian(client, create_user):
    user=create_user
    client.login(username=user.username, password='password123')    
    response = client.get(reverse('add_book'))
    assert response.status_code == 403

@pytest.mark.django_db
def test_borrow_book_view(client, create_user, create_book):
    user=create_user
    client.login(username=user.username,password='password123')
    book=create_book
    response = client.post(reverse('borrow_book', kwargs={'pk': book.pk}))
    assert response.status_code == 302
    assert BorrowedBook.objects.filter(book=book, user=user).exists()
    assert Book.objects.get(pk=book.pk).available_copies == 9

@pytest.mark.django_db
def test_borrow_already_borrowed_book(client, create_user,create_book):
    user=create_user
    client.login(username=user.username, password='password123')
    book = create_book
    BorrowedBook.objects.create( borrowed_date=timezone.now().date(),
        due_date=timezone.now().date() + timezone.timedelta(days=1),
        return_status=False,
        book=book,
        user=user
    )
    response = client.post(reverse('borrow_book', kwargs={'pk': book.pk}))
    assert response.status_code == 302
    messages = list(get_messages(response.wsgi_request))
    assert any(str(message) == "You have already borrowed this book." for message in messages)
    assert BorrowedBook.objects.filter(book=book, user=user).count() == 1

@pytest.mark.django_db
def test_borrow_with_overdue_books(client, create_user, create_book):
    user = create_user
    client.login(username=user.username, password='password123')
    book=create_book
    BorrowedBook.objects.create(
        borrowed_date=timezone.now().date() - timezone.timedelta(days=10),
        due_date=timezone.now().date() - timezone.timedelta(days=5),
        return_status=False,
        book=book,
        user=user
    )
    new_book = create_book
    response = client.post(reverse('borrow_book', kwargs={'pk': new_book.pk}))
    assert response.status_code == 302
    messages = list(get_messages(response.wsgi_request))
    assert any(str(message) == "You have overdue books. Please return them before borrowing new books." for message in messages)

@pytest.mark.django_db
def test_return_book_view(client, create_user, create_book):
    user = create_user
    book = create_book
    test_borrow_book_view(client, create_user, create_book)
    borrowed_book = BorrowedBook.objects.get(book=book, user=user)
    penalty = Penalty.objects.create(
        borrowed_book=borrowed_book,
        fine_amount=1.00,
        payment_status='paid'
    )
    response = client.post(reverse('return_book',kwargs={'pk':borrowed_book.id}))
    borrowed_book.refresh_from_db()
    book.refresh_from_db()
    assert response.status_code == 302
    assert borrowed_book.return_status == True
    assert book.available_copies == 10
    assert Penalty.objects.filter(borrowed_book = borrowed_book).exists()

@pytest.mark.django_db
def test_penalty_payment_view(client, create_user,create_book):
    user = create_user
    client.login(username=user.username, password='password123')
    book=create_book
    test_borrow_book_view(client, create_user, create_book)
    borrowed_book = BorrowedBook.objects.get(book=book, user=user)

    penalty = Penalty.objects.create(
        fine_amount=1.00,
        payment_status='unpaid',
        borrowed_book=borrowed_book
    )
    response = client.post(reverse('penalty_payment', kwargs={'pk': penalty.pk}))
    assert response.status_code == 302 
    assert Penalty.objects.get(pk=penalty.pk).payment_status == 'paid'

@pytest.mark.django_db
def test_activity_page_view(client, create_user):
    user = create_user
    client.login(username=user.username, password="password123")
    response = client.get(reverse('activity_page'))
    assert response.status_code == 200 

@pytest.mark.django_db
def test_library_activity_page_view(client, create_librarian):
    librarian = create_librarian
    client.login(username=librarian.username, password='password456')
    response = client.get(reverse('library_activity'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_book_list_view(client, create_book):
    book=create_book
    response = client.get(reverse('book-list'))
    assert response.status_code == 200
    assert 'books_list' in response.context
    assert len(response.context['books_list']) == 1

@pytest.mark.django_db
def test_book_detail_view(client, create_book):
    response = client.get(reverse('book_detail', kwargs={'pk': create_book.pk}))
    assert response.status_code == 200
    assert 'book' in response.context
    assert response.context['book'] == create_book

@pytest.mark.django_db
def test_book_update_view(client, create_book,create_genre,create_author):
    genre=create_genre
    author=create_author
    updated_data = {
        'title': 'Updated Book Title',
        'isbn': '1234567890124',
        'publication_year': 2021,
        'available_copies': 15,
        'genres': [genre.id],
        'authors':[author.id]
    }
    response = client.post(reverse('book_update', kwargs={'pk': create_book.pk}), updated_data)
    assert response.status_code == 302
    updated_book = Book.objects.get(pk=create_book.pk)
    assert updated_book.title == 'Updated Book Title'
    assert updated_book.isbn == '1234567890124'
    assert updated_book.publication_year == 2021
    assert updated_book.available_copies == 15

@pytest.mark.django_db
def test_delete_book_(client, create_librarian, create_book):
    librarian = create_librarian
    client.login(username=librarian.username, password='password456')
    response = client.post(reverse('delete', args=[create_book.id]))
    assert response.status_code == 302  
    assert not Book.objects.filter(id=create_book.id).exists()

@pytest.mark.django_db
def test_edit_borrowed_book_view(client, create_librarian, create_book, create_user):
    librarian = create_librarian
    client.login(username=librarian.username, password='password456')
    book = create_book
    user = create_user
    borrowed_book = BorrowedBook.objects.create(
        borrowed_date=timezone.now().date(),
        due_date=timezone.now().date() + timezone.timedelta(days=7),
        return_status=False,
        book=book,
        user=user
    )

    penalty = Penalty.objects.create(
        borrowed_book=borrowed_book,
        fine_amount=5.00,
        payment_status='unpaid'
    )

    updated_data = {
        'borrowed_date': borrowed_book.borrowed_date,
        'due_date': borrowed_book.due_date,
        'return_status': True,
        'penalty_status': 'paid' }
    response = client.post(reverse('edit_borrowed_book', kwargs={'pk': borrowed_book.pk}), updated_data)

    borrowed_book.refresh_from_db()
    penalty.refresh_from_db()

    assert response.status_code == 302  
    assert borrowed_book.return_status is True
    assert penalty.payment_status == 'paid'