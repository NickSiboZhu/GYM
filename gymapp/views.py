from django.shortcuts import render, redirect
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, render
from .models import Choice, Question
from django.urls import reverse
from django.contrib.auth import authenticate, login
from manager.models import Manager
from manager.models import Customer
from django.contrib.auth.hashers import make_password
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
import mysql.connector


def index(request):
    return render(request, "index.html")

def home(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")


def login(request):
    error = 'none'
    if request.method == 'POST':
        username = request.POST['uname']
        password = request.POST['pwd']
        user_type = request.POST['user_type']

        if user_type == 'manager':
            try:
                manager = Manager.objects.get(account=username, password=password)
                if manager:
                    request.session['manager_id'] = manager.Manager_id
                    return redirect(reverse('manager:manager_dashboard'))
            except Manager.DoesNotExist:
                error = 'yes'

        elif user_type == 'customer':
            try:
                customer = Customer.objects.get(account=username, password=password)
                if customer:
                    request.session['customer_id'] = customer.Customer_id
                    return redirect(reverse('customer_dashboard'))
            except Customer.DoesNotExist:
                error = 'yes'

    return render(request, 'login.html', {'error': error})


def customer_registration(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        sex = request.POST['sex']
        ph_num = request.POST['phone']
        avatar = request.FILES['avatar'].read()
        account = request.POST['account']
        password = request.POST['password']
        balance = 0

        # Connect to database
        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
        cursor = cnx.cursor()

        # Insert data into Customer table
        query = ("INSERT INTO Customer (sex, first_name, last_name, ph_num, avatar, account, password, balance) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        values = (sex, first_name, last_name, ph_num, avatar, account, password, balance)
        cursor.execute(query, values)

        # Commit changes and close database connection
        cnx.commit()
        cursor.close()
        cnx.close()

        # Redirect to customer dashboard
        return redirect(reverse('customer_dashboard'))
    else:
        return render(request, 'customer_registration.html')


def content(request):
    return render(request, "contact.html")

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "detail.html", {"question": question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "results.html", {"question": question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("gymapp:results", args=(question.id,)))

