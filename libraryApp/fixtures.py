import pytest
from .models import CustomUser, Genre, Author,Book
@pytest.fixture
def create_user(db):
    user = CustomUser.objects.create(username='testuser', role='user', mobile_number='1234567890', address='address1')
    user.set_password('password123')
    user.save()
    return user

@pytest.fixture
def create_librarian(db):
    librarian = CustomUser.objects.create(username='testuser2', role='librarian', mobile_number='0987654321', address='address2')
    librarian.set_password('password456')
    librarian.save()
    return librarian

@pytest.fixture
def create_genre(db):
    return Genre.objects.create(name='Science Fiction')

@pytest.fixture
def create_author(db):
    return Author.objects.create(name='John Doe', date_of_birth='1981-01-01', nationality='American')

@pytest.fixture
def create_book(db, create_genre, create_author):
    book = Book.objects.create(title='Sample Book', isbn='2345678', publication_year='2001', available_copies=10)
    book.genres.add(create_genre)
    book.authors.add(create_author)
    return book