from django.core.files.storage import FileSystemStorage
import base64
from django.db.backends import mysql
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.cache import cache_page, never_cache
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection
from django.core.files.base import ContentFile
from django.http import JsonResponse
import mysql.connector

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gym"
    )
def supplements(request):
    # Connect to the database
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
    cursor = cnx.cursor()

    # Fetch data from the Supplement table
    query = "SELECT * FROM Supplements"
    cursor.execute(query)
    supplements_raw = cursor.fetchall()

    # Convert the fetched data into a list of dictionaries for easier handling in the template
    supplements = []
    for supplement_raw in supplements_raw:
        supplements.append({
            'id': supplement_raw[0],
            'name': supplement_raw[1],
            'price': supplement_raw[3],
            'stock': supplement_raw[4],
            'image': base64.b64encode(supplement_raw[2]).decode('utf-8')
        })

    # Close the database connection
    cursor.close()
    cnx.close()

    # Pass data to the template context
    context = {'supplements': supplements}

    return render(request, 'manager/supplements.html', context)




def equipment(request):
    # Connect to the database
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
    cursor = cnx.cursor()

    # Fetch data from Equipment, have, and Block tables
    query = """
        SELECT e.E_id, e.name, b.B_id, b.type, b.image
        FROM Equipment e
        JOIN have h ON e.E_id = h.E_id
        JOIN Block b ON h.B_id = b.B_id;
    """
    cursor.execute(query)
    equipment = cursor.fetchall()

    # Close database connection
    cursor.close()
    cnx.close()

    equipment_base64 = []
    for item in equipment:
        image_data = base64.b64encode(item[4]).decode('utf-8')
        equipment_base64.append((*item[:-1], image_data))

    # Pass data to template context
    context = {'equipment': equipment_base64}

    return render(request, 'manager/equipment.html', context)


def coaches(request):
    # Connect to database
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
    cursor = cnx.cursor()

    # Fetch data from Coach table
    query = "SELECT * FROM Coach"
    cursor.execute(query)
    coaches = cursor.fetchall()

    # Close database connection
    cursor.close()
    cnx.close()

    coaches_base64 = []
    for coach in coaches:
        image_data = base64.b64encode(coach[5]).decode('utf-8')
        coaches_base64.append((*coach[:-1], image_data))

    # Pass data to template context
    context = {'coaches': coaches_base64}

    return render(request, 'manager/coaches.html', context)




def courses(request):
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
    cursor = cnx.cursor()

    query = """
        SELECT c.Course_id, c.name, c.time, co.first_name, co.last_name, b.type, b.image
        FROM Course c
        JOIN Coach co ON c.Coach_id = co.Coach_id
        JOIN Block b ON c.B_id = b.B_id
    """
    cursor.execute(query)
    courses_raw = cursor.fetchall()

    courses = []
    for course in courses_raw:
        courses.append({
            'id': course[0],
            'name': course[1],
            'time': course[2],
            'coach_name': f"{course[3]} {course[4]}",
            'block_name': course[5],
            'block_image': base64.b64encode(course[6]).decode('utf-8')
        })

    cursor.close()
    cnx.close()

    context = {'courses': courses}
    return render(request, 'manager/courses.html', context)




def membership_cards(request):
    # Connect to the database
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
    cursor = cnx.cursor()

    # Fetch data from the Membership and Customer tables
    query = """
    SELECT m.Customer_id, c.first_name, c.last_name, c.account, m.start_date, m.end_date
    FROM Member m
    JOIN Customer c ON m.Customer_id = c.Customer_id
    """
    cursor.execute(query)
    memberships_raw = cursor.fetchall()

    # Convert the fetched data into a list of dictionaries for easier handling in the template
    memberships = []
    for membership in memberships_raw:
        memberships.append({
            'customer_id': membership[0],
            'first_name': membership[1],
            'last_name': membership[2],
            'account': membership[3],
            'start_date': membership[4],
            'end_date': membership[5]
        })

    # Close the database connection
    cursor.close()
    cnx.close()

    # Pass data to the template context
    context = {'memberships': memberships}

    return render(request, 'manager/membership_cards.html', context)



def manager_dashboard(request):
    return render(request, 'manager/manager_dashboard.html')


def data_visual(request):
    # Connect to the database
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
    cursor = cnx.cursor()

    # Fetch the count of coaches, supplements, equipment, and personal_information
    query_coach = "SELECT COUNT(*) FROM Coach"
    query_supplements = "SELECT COUNT(*) FROM Supplements"
    query_equipment = "SELECT COUNT(*) FROM Equipment"  # Replace 'Equipment' with the correct table name
    query_customer = "SELECT COUNT(*) FROM Customer"  # Replace 'Personal_Information' with the correct table name

    cursor.execute(query_coach)
    coach_count = cursor.fetchone()[0]

    cursor.execute(query_supplements)
    supplements_count = cursor.fetchone()[0]

    cursor.execute(query_equipment)
    equipment_count = cursor.fetchone()[0]

    cursor.execute(query_customer)
    customer_count = cursor.fetchone()[0]

    # Close the database connection
    cursor.close()
    cnx.close()

    # Pass data to the template context
    context = {
        'coach_count': coach_count,
        'supplements_count': supplements_count,
        'equipment_count': equipment_count,
        'customer_count': customer_count,
    }

    return render(request, 'manager/data_visual.html', context)


def personal_info(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Customer")
        customers = cursor.fetchall()

    context = {'customers': customers}
    return render(request, 'manager/personal_info.html', context)


def add_coach(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        sex = request.POST['sex']
        ph_num = request.POST['phone']
        avatar = request.FILES['avatar'].read()

        # Connect to database
        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
        cursor = cnx.cursor()

        # Insert data into Coach table
        query = ("INSERT INTO Coach (sex, first_name, last_name, ph_num, avatar) "
                 "VALUES (%s, %s, %s, %s, %s)")
        values = (sex, first_name, last_name, ph_num, avatar)
        cursor.execute(query, values)

        # Commit changes and close database connection
        cnx.commit()
        cursor.close()
        cnx.close()

        # Redirect to coaches list
        return redirect(reverse('manager:coaches'))
    else:
        return render(request, 'manager/add_coach.html')


def delete_coach(request, coach_id):
    if request.method == 'POST':
        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
        cursor = cnx.cursor()

        query = "DELETE FROM Coach WHERE coach_id = %s"
        cursor.execute(query, (coach_id,))

        cnx.commit()
        cursor.close()
        cnx.close()
        return redirect(reverse('manager:coaches'))
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def add_supplement(request):
    if request.method == 'POST':
        name = request.POST['name']
        price = request.POST['price']
        stock = int(request.POST['stock'])
        image = request.FILES['image'].read()

        # Connect to the database
        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
        cursor = cnx.cursor()

        # Check if the supplement with the same name already exists
        query = "SELECT * FROM Supplements WHERE name = %s"
        cursor.execute(query, (name,))
        existing_supplement = cursor.fetchone()

        if existing_supplement:
            # Update the stock
            query = "UPDATE Supplements SET stock = stock + %s WHERE name = %s"
            cursor.execute(query, (stock, name))
        else:
            # Insert data into the Supplement table
            query = "INSERT INTO Supplements (name, price, stock, image) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, price, stock, image))

        # Commit the transaction and close the database connection
        cnx.commit()
        cursor.close()
        cnx.close()

    return redirect(reverse('manager:supplements'))



def delete_supplement(request, supplement_id):
    if request.method == 'POST':
        # Connect to the database
        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
        cursor = cnx.cursor()

        # Delete the supplement from the Supplement table
        query = "DELETE FROM Supplements WHERE S_id = %s"
        cursor.execute(query, (supplement_id,))

        # Commit the transaction and close the database connection
        cnx.commit()
        cursor.close()
        cnx.close()

    return redirect(reverse('manager:supplements'))

def update_supplement_stock(request, supplement_id):
    if request.method == 'POST':
        stock = int(request.POST['stock'])

        # Connect to the database
        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
        cursor = cnx.cursor()

        # Update the supplement stock
        query = "UPDATE Supplements SET stock = %s WHERE S_id = %s"
        cursor.execute(query, (stock, supplement_id))

        # Commit the transaction and close the database connection
        cnx.commit()
        cursor.close()
        cnx.close()

    return redirect(reverse('manager:supplements'))

def update_supplement_price(request, supplement_id):
    if request.method == 'POST':
        new_price = request.POST['new_price']

        # Connect to the database
        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
        cursor = cnx.cursor()

        # Update the price of the supplement
        query = "UPDATE Supplements SET price = %s WHERE S_id = %s"
        cursor.execute(query, (new_price, supplement_id))

        # Commit the transaction and close the database connection
        cnx.commit()
        cursor.close()
        cnx.close()

    return redirect(reverse('manager:supplements'))

def add_course(request):
    if request.method == 'POST':
        name = request.POST['name']
        time = request.POST['time']
        coach_id = request.POST['coach_id']
        block_id = request.POST['block_id']

        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
        cursor = cnx.cursor()

        # Check if coach_id exists
        coach_query = "SELECT * FROM Coach WHERE Coach_id = %s"
        cursor.execute(coach_query, (coach_id,))
        coach = cursor.fetchone()

        if not coach:
            cursor.close()
            cnx.close()
            return JsonResponse({"status": "error", "message": "Coach does not exist"})

        # Check if block_id exists
        block_query = "SELECT * FROM Block WHERE B_id = %s"
        cursor.execute(block_query, (block_id,))
        block = cursor.fetchone()

        if not block:
            cursor.close()
            cnx.close()
            return JsonResponse({"status": "error", "message": "Block does not exist"})

        query = "INSERT INTO Course (name, time, Coach_id, B_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, time, coach_id, block_id))

        cnx.commit()
        cursor.close()
        cnx.close()

        return redirect(reverse('manager:courses'))
    return redirect(reverse('manager:courses'))

def delete_course(request, course_id):
    if request.method == 'POST':
        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
        cursor = cnx.cursor()

        query = "DELETE FROM Course WHERE Course_id = %s"
        cursor.execute(query, (course_id,))

        cnx.commit()
        cursor.close()
        cnx.close()

    return redirect(reverse('manager:courses'))

def add_equipment(request):
    if request.method == "POST":
        equipment_name = request.POST['name']
        block_id = request.POST['block_id']

        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
        cursor = cnx.cursor()

        # Check if block exists
        query = "SELECT * FROM Block WHERE B_id=%s"
        cursor.execute(query, (block_id,))
        block = cursor.fetchone()

        if block:
            query = "INSERT INTO Equipment (name) VALUES (%s)"
            cursor.execute(query, (equipment_name,))
            equipment_id = cursor.lastrowid

            query = "INSERT INTO have (B_id, E_id) VALUES (%s, %s)"
            cursor.execute(query, (block_id, equipment_id))
            cnx.commit()

            cursor.close()
            cnx.close()

            return redirect(reverse('manager:equipment'))
        else:
            cursor.close()
            cnx.close()
            return JsonResponse({"status": "error", "message": "Block does not exist"})

def delete_equipment(request, equipment_id):
    if request.method == "POST":
        cnx = mysql.connector.connect(user='root', password='', host='localhost', database='gym')
        cursor = cnx.cursor()

        query = "DELETE FROM have WHERE E_id=%s"
        cursor.execute(query, (equipment_id,))

        query = "DELETE FROM Equipment WHERE E_id=%s"
        cursor.execute(query, (equipment_id,))

        cnx.commit()

        cursor.close()
        cnx.close()

        return redirect(reverse('manager:equipment'))
