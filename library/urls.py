from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),

    #books related mapping
    path("books/", views.books_home, name='books_home'),
    path("add_books/", views.add_books, name='add_books'),
    path("issue_book/", views.issue_book, name='issue_book'),
    path("return_book/",views.return_book,name='return_book'),
    path('show_book_detail/<str:pk>', views.show_book_detail,name='show_book_detail'),
    path('delete_book/<str:pk>', views.delete_book, name='delete_book'),
    path('confirm_delete_book/<str:pk>', views.confirm_delete_book,name='confirm_delete_book'),


    #members related mapping
    path("members/", views.members_home, name='members_home'),
    path("add_member/", views.add_member, name='add_member'),
    path("delete_member/<str:pk>", views.delete_member, name='delete_member'),
    path("clear_debt/", views.clear_debt, name='clear_debt'),
    path("confirm_debt_clear/<str:pk>", views.confirm_debt_clear, name='confirm_debt_clear'),
    path("confirm_delete_member/<str:pk>", views.confirm_delete_member, name='confirm_delete_member'),
    path("members_detail/<str:pk>", views.members_detail, name='members_detail')

]