from django.urls import path, re_path
from .  import views
from django import views as django_views
from django.views.i18n import JavaScriptCatalog
urlpatterns = [

    path('', views.home,name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login' ),
    path('logout/', views.logout_view, name='logout' ),
    path('add-book/', views.AddBookView.as_view(), name='add_book'),
    # re_path(r'^jsi18n/$', django_views.i18n.JavaScriptCatalog.as_view(), name='jsi18n'),
    re_path(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='jsi18n'),
    path('books/',views.BookListView.as_view(),name='book-list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('books/author/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    path('profile/', views.profile_view, name='profile'),
    path('books/<int:pk>/delete/', views.delete_book, name='delete'),
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('books/<int:pk>/borrow/', views.borrow_book_view, name='borrow_book'),
    path('activity/', views.activity_page_view, name='activity_page'),
    path('activity/return/<int:pk>/', views.return_book_view, name='return_book'),
    path('library-activity/', views.library_activity_page, name='library_activity'),
    path('penalty/payment/<int:pk>/', views.penalty_payment_view, name='penalty_payment'),
    path('library-activity/<int:pk>/edit/', views.edit_borrowed_book, name='edit_borrowed_book'),
    
]
