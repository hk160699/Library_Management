from django.test import TestCase
from . models import CustomUser,Genre, Author,Book, BorrowedBook
from django.utils import timezone
from datetime import timedelta
class libraryAppTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username = 'testuser', password='password123', role = 'user', mobile_number='1234567890', address='address1')
        self.librarian = CustomUser.objects.create(username='testuser2',password='password456', role='librarian', mobile_number='0987654321',address='address2')
        self.genre = Genre.objects.create(name='Science Fiction')
        self.author = Author.objects.create(name='John Doe', date_of_birth = '1980-01-01', nationality='American')
        self.book=Book.objects.create(title = 'Sample Book', isbn='1234567', publication_year=2024, available_copies=5)
        self.book.genres.add(self.genre)
        self.book.authors.add(self.author)

        self.borrowed_book = BorrowedBook.objects.create(borrowed_date=timezone.now().date(), due_date=timezone.now().date() + timedelta(days=7), book = self.book, user=self.user)

    def test_book_creation(self):
        book = Book.objects.get(isbn='1234567')
        self.assertEqual(book.title, 'Sample Book')
        self.assertIn(self.genre, book.genres.all())
        self.assertIn(self.author, book.authors.all())