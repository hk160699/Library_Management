from django.contrib import admin

from libraryApp.forms import AddBookForm
from .models import CustomUser, Author, Genre, Book, BorrowedBook, Penalty
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Genre)
admin.site.register(Author)
# admin.site.register(Book)
admin.site.register(BorrowedBook)
admin.site.register(Penalty)

class BookAdmin(admin.ModelAdmin):
    class Meta:
        model = Book
        fields = '__all__'
    filter_horizontal = ('authors', 'genres')  

admin.site.register(Book, BookAdmin)

