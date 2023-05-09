from _decimal import Decimal
from datetime import timedelta, datetime

from django.http import HttpResponse
from django.urls import reverse

from django.shortcuts import render, redirect
import mysql.connector
from django.http import JsonResponse
import json
import base64
from django.views.decorators.csrf import csrf_exempt



def show(request):
    return render(request,"customer.html")

def showc(request):
    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1', database='gym')
    cursor = cnx.cursor()

    cursor.execute('SELECT Coach_id,sex,first_name,last_name,avatar,ph_num FROM gym.coach')
    data = cursor.fetchall()

    data_list = []
    for row in data:
        # Assuming the 'image' column contains binary image data as BLOB type in MySQL
        image_data = base64.b64encode(row[4]).decode('utf-8')  # Convert binary data to base64-encoded string
        data_list.append(
            {'Coach_id': row[0], 'sex': row[1], 'first_name': row[2], 'last_name': row[3], 'avatar': image_data,
             'PHONE': row[5]})

    cursor.close()
    cnx.close()

    context = {
        'data': data_list,
    }

    return render(request, "coaches.html", context)


def showcommodities(request):
    # Get current customer ID
    customer_id = request.session['customer_id']

    print("Customer ID: ", customer_id)  # Debug print

    # Connect to database
    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1', database='gym')

    # Create a cursor object
    cursor = cnx.cursor()

    # Retrieve current balance from database
    query = "SELECT balance FROM Customer WHERE Customer_id=%s"
    cursor.execute(query, (customer_id,))
    current_balance = cursor.fetchone()[0]
    print("Current Balance: ", current_balance)  # Debug print

    # 展示商品
    cursor.execute('SELECT S_id, name, image, price, stock FROM gym.supplements')
    data = cursor.fetchall()

    data_list = []
    for row in data:
        # Assuming the 'image' column contains binary image data as BLOB type in MySQL
        image_data = base64.b64encode(row[2]).decode('utf-8')  # Convert binary data to base64-encoded string
        data_list.append({'S_id': row[0], 'name': row[1], 'image': image_data, 'price': row[3], 'stock': row[4]})

    query = "SELECT b.Customer_id, b.S_id, b.number, s.name, s.price FROM buy b \
                         INNER JOIN gym.supplements s ON b.S_id = s.S_id \
                         WHERE b.Customer_id = %s "
    cursor = cnx.cursor()
    cursor.execute(query, (customer_id,))
    supple = cursor.fetchall()

    # Close database connection and cursor
    cursor.close()
    cnx.close()

    # Pass the balance to the context
    context = {'balance': current_balance,
               'data': data_list,
               'supple': supple,
               }

    return render(request, "commodities.html", context)

def showequipment(request):
    return render(request,"c_equipment.html")


def showcards(request):
    # Replace this with the actual customer_id of the logged-in user
    customer_id = request.session['customer_id']

    context = {
        'customer_id': customer_id,
    }

    return render(request, "c_cards.html", context)


def register_membership(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        data = json.loads(request.body)

        # Get the required information from the parsed data
        customer_id = request.session['customer_id']
        membership_type = data['membership_type']

        # Convert membership_type to proper case
        membership_type = membership_type.capitalize()

        # Determine the membership duration and price based on the membership type
        if membership_type == 'Junior':
            duration = timedelta(days=180)
            price = 500
        elif membership_type == 'Senior':
            duration = timedelta(days=365)
            price = 1000
        else:
            return JsonResponse({"success": False, "error": "Invalid membership type"})

        # Connect to the database
        cnx = mysql.connector.connect(user='root', password='',
                                      host='localhost', database='gym')

        # Create a cursor object
        cursor = cnx.cursor()

        # Check if the customer has enough balance to purchase the membership
        query = "SELECT balance FROM Customer WHERE Customer_id=%s"
        cursor.execute(query, (customer_id,))
        balance = cursor.fetchone()[0]

        if balance < price:
            cursor.close()
            cnx.close()
            return JsonResponse({"success": False, "error": "Insufficient balance"})

        # Update the customer's balance
        new_balance = balance - price
        query = "UPDATE Customer SET balance=%s WHERE Customer_id=%s"
        cursor.execute(query, (new_balance, customer_id))

        # Calculate the start and end date of the membership
        start_date = datetime.now()
        end_date = start_date + duration

        # Insert the membership record into the Member table
        query = "INSERT INTO Member (Customer_id, start_date, end_date) VALUES (%s, %s, %s)"
        cursor.execute(query, (customer_id, start_date, end_date))

        # Commit the changes and close the connection
        cnx.commit()
        cursor.close()
        cnx.close()

        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"})



def showblock(request):
    cnx = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1', database='gym')
    cursor = cnx.cursor()

    cursor.execute('SELECT B_id,type,image FROM block')
    blocks = cursor.fetchall()

    data_list = []
    for block in blocks:
        cursor.execute('SELECT equipment.name FROM equipment JOIN have ON equipment.E_id=have.E_id WHERE have.B_id=%s',
                       (block[0],))
        equipment = cursor.fetchall()
        equipment_list = [e[0] for e in equipment]

        # Assuming the 'image' column contains binary image data as BLOB type in MySQL
        image_data = base64.b64encode(block[2]).decode('utf-8')  # Convert binary data to base64-encoded string
        data_list.append({'B_id': block[0], 'type': block[1], 'image': image_data, 'equipment': equipment_list})

    cursor.close()
    cnx.close()

    context = {'data': data_list}
    return render(request, "c_block.html", context)

def showcourses(request):
    # Replace this with the actual customer_id of the logged-in user
    customer_id = request.session['customer_id']

    # Connect to the database
    cnx = mysql.connector.connect(user='root', password='',
                                  host='localhost', database='gym')

    # Create a cursor object
    cursor = cnx.cursor()

    # Query course information
    query = """SELECT Course.Course_id, Course.name, Course.time, 
                      Coach.first_name, Coach.last_name, Block.type
               FROM Course
               INNER JOIN Coach ON Course.Coach_id = Coach.Coach_id
               INNER JOIN Block ON Course.B_id = Block.B_id"""
    cursor.execute(query)
    courses = cursor.fetchall()

    # Close the connection
    cursor.close()
    cnx.close()

    context = {
        'customer_id': customer_id,
        'courses': courses,
    }

    return render(request,"courses.html", context)

@csrf_exempt
def select_course(request):
    if request.method == 'POST':
        customer_id = request.session['customer_id']
        course_id = request.POST['course_id']

        # Connect to the database
        cnx = mysql.connector.connect(user='root', password='',
                                      host='localhost', database='gym')

        # Create a cursor object
        cursor = cnx.cursor()

        # Check if the customer is a member
        query = "SELECT * FROM Member WHERE Customer_id=%s"
        cursor.execute(query, (customer_id,))
        is_member = cursor.fetchone()

        if not is_member:
            cursor.close()
            cnx.close()
            return JsonResponse({"success": False, "error": "You must be a gym member to select a course."})

            # Insert the course selection into the select_course table
        query = "INSERT INTO select_course (Customer_id, Course_id) VALUES (%s, %s)"
        cursor.execute(query, (customer_id, course_id))

        # Commit the changes and close the connection
        cnx.commit()
        cursor.close()
        cnx.close()

        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"})


def showorder(request):
    return render(request,"c_order.html")




# Function to get and update customer balance
def update_balance(request):
    # Get current customer ID
    customer_id = request.session['customer_id']

    # Connect to database
    cnx = mysql.connector.connect(user='root', password='',
                                  host='localhost', database='gym')

    # Create a cursor object
    cursor = cnx.cursor()

    # Retrieve current balance from database
    query = "SELECT balance FROM Customer WHERE Customer_id=%s"
    cursor.execute(query, (customer_id,))
    current_balance = cursor.fetchone()[0]

    # Get amount to add from form data
    amount = request.POST.get('amount')

    # Calculate new balance
    new_balance = current_balance + Decimal(amount)

    # Update balance in database
    query = "UPDATE Customer SET balance=%s WHERE Customer_id=%s"
    cursor.execute(query, (new_balance, customer_id))
    cnx.commit()

    # Close database connection and cursor
    cursor.close()
    cnx.close()

    # Redirect to customer home page
    return redirect(reverse('commodities'))

def purchase(request):
    customer_id = request.session['customer_id']

    s_id = request.POST.get('supplement_id')

    if request.method == 'POST':
        cnx = mysql.connector.connect(user='root', password='',
                                      host='127.0.0.1',
                                      database='gym',
                                      buffered=True
                                      )
        cursor = cnx.cursor()

        # 获取补品价格信息
        query = "SELECT price FROM Supplements WHERE S_id = %s"
        cursor.execute(query, (s_id,))
        row = cursor.fetchone()
        if row is not None:
            price = row[0]
        else:
            price = 10

        # 获取库存
        query = "SELECT stock FROM Supplements WHERE S_id = %s"
        cursor.execute(query, (s_id,))
        row1 = cursor.fetchone()
        if row1 is not None:
            stock = row1[0]
        else:
            stock = 100

        # 获取会员信息
        query = "SELECT balance FROM Customer WHERE Customer_id = %s"
        cursor.execute(query, (customer_id,))
        balance = cursor.fetchone()[0]

        # 检查余额是否足够购买
        if balance >= price and stock > 0:
            # 更新余额
            new_balance = balance - price
            query = "UPDATE Customer SET balance = %s WHERE Customer_id = %s"
            cursor.execute(query, (new_balance, customer_id))

            # 更新库存
            new_stock = stock - 1
            query = "UPDATE gym.supplements SET stock = %s WHERE gym.supplements.S_id = %s"
            cursor.execute(query, (new_stock, s_id))

            query = "SELECT Customer_id,S_id FROM gym.buy WHERE Customer_id = %s AND S_id = %s"
            cursor.execute(query, (customer_id,s_id))
            nowid = cursor.fetchall()

            if nowid:
               query = "SELECT number FROM gym.buy WHERE Customer_id = %s AND S_id = %s"
               cursor.execute(query, (customer_id, s_id))
               num = cursor.fetchone()[0]
               num = num + 1
               query = "UPDATE gym.buy SET number = %s WHERE Customer_id = %s AND S_id = %s"
               cursor.execute(query, (num, customer_id, s_id))
            else:
                num = 1
                query = "INSERT INTO buy(gym.buy.customer_id, gym.buy.s_id, gym.buy.number) VALUES (%s , %s, %s)"
                cursor.execute(query, (customer_id, s_id, num))






            cnx.commit()
            cursor.close()
            cnx.close()

        return redirect(reverse('commodities'))



def showpp(request):
    customer_id = request.session['customer_id']
    cnx = mysql.connector.connect(user='root', password='',
                                  host='localhost', database='gym')

    # Create a cursor object
    cursor = cnx.cursor()
    query = "SELECT Customer_id,sex,first_name,last_name,ph_num,avatar,account,password,balance FROM Customer WHERE Customer_id=%s"
    cursor.execute(query, (customer_id,))
    data = cursor.fetchall()
    data_list = []
    for row in data:
        # Assuming the 'image' column contains binary image data as BLOB type in MySQL
        image_data = base64.b64encode(row[5]).decode('utf-8')  # Convert binary data to base64-encoded string
        data_list.append(
            {'Customer_id': row[0], 'sex': row[1], 'first_name': row[2], 'last_name': row[3], 'ph_num': row[4],
             'avatar': image_data, 'account': row[6], 'password': row[7], 'balance': row[8]})

    query = "SELECT c.first_name, c.last_name, co.name, co.time, ch.first_name, ch.last_name FROM Customer c \
                   INNER JOIN select_course sc ON c.Customer_id = sc.Customer_id \
                   INNER JOIN Course co ON sc.Course_id = co.Course_id \
                   INNER JOIN Coach ch ON co.Coach_id = ch.Coach_id \
                   WHERE c.Customer_id = %s "
    cursor = cnx.cursor()
    cursor.execute(query, (customer_id,))
    results = cursor.fetchall()

    query = "SELECT b.Customer_id, b.S_id, b.number, s.name,s.price FROM buy b \
                      INNER JOIN gym.supplements s ON b.S_id = s.S_id \
                      WHERE b.Customer_id = %s "
    cursor = cnx.cursor()
    cursor.execute(query, (customer_id,))
    supple = cursor.fetchall()

    cursor.close()
    cnx.close()

    context = {'data': data_list,
               'result': results,
               'supple': supple}

    return render(request, "c_personal_info.html", context)







