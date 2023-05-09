from django.urls import path

from . import views

app_name = "gymapp"
urlpatterns = [
    path("", views.index, name="index"),

    path("home/",views.home, name="home"),

    path("about/", views.about, name="about"),

    path("login/", views.login, name="login"),

    path("content/", views.content, name = "content"),

    path('register/', views.customer_registration, name='customer_registration'),

    # ex: /polls/5/
    path("<int:question_id>/", views.detail, name="detail"),

    # ex: /polls/5/results/
    path("<int:question_id>/results/", views.results, name="results"),
    # ex: /polls/5/vote/
    path("<int:question_id>/vote/", views.vote, name="vote"),
]