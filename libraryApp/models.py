from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from .enums import Role, PaymentStatus

# Create your models here.
class CustomUser(AbstractUser):
    role = models.CharField(max_length=10, choices=Role.choices(), default=Role.USER)
    mobile_number = models.CharField(max_length=15)
    address = models.TextField()

class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Author(models.Model):
    name = models.CharField(max_length=64)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=32)

    def __str__(self):
        return self.name           

class Book(models.Model):
    title = models.CharField(max_length=128)
    isbn = models.CharField(max_length=32, unique=True)
    publication_year = models.IntegerField()
    available_copies = models.IntegerField(validators = [MinValueValidator(1)])
    cover_image = models.ImageField(upload_to='book_images/', default='book_images/default_image.jpg', max_length=200)
    genres = models.ManyToManyField(Genre, related_name='genre_books')
    authors = models.ManyToManyField(Author, related_name='books')

    def __str__(self):
        return self.title
    
class BorrowedBook(models.Model):
    borrowed_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    return_status = models.BooleanField(default=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowed_by')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='borrowed_books')
  
    def __str__(self):
        return f"{self.book.title} borrowed by {self.user.username}"
    
class Penalty(models.Model):
    payment_status = models.CharField(max_length=10, choices=PaymentStatus.choices(), default=PaymentStatus.UNPAID)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(null=True, blank=True)
    borrowed_book = models.OneToOneField(BorrowedBook, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Penalty status for {self.borrowed_book.user.username} is {self.payment_status}"
    