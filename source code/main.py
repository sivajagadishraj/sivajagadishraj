import datetime

from bson import ObjectId
from flask import Flask, render_template, request, session, redirect
import pymongo
import os
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
PIC_PATH = APP_ROOT + "/static/pic"
app = Flask(__name__)
app.secret_key = "project"
my_client = pymongo.MongoClient("mongodb://localhost:27017")
my_db = my_client["hotel_room_reservation"]
admin_collection = my_db["admin"]
staff_collection = my_db["staff"]
customer_collection = my_db["customer"]
room_collection = my_db["room"]
room_type_collection = my_db["room_type"]
reservations_collection = my_db["reservations"]
payment_transactions_collection = my_db["payment_transactions"]
pic_collection = my_db['pic']
count = admin_collection.count_documents({})
if count == 0:
    query = {"password": "admin", "username":"admin", "email":"admin@gmail.com", "first_name":"admin", "last_name":"admin"}
    admin_collection.insert_one(query)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    query = {"username":username, "password":password}
    count = admin_collection.count_documents(query)
    if count > 0:
        admin = admin_collection.find_one(query)
        session['admin_id'] = str(admin['_id'])
        session['role'] = 'admin'
        return redirect("/admin_home")
    else :
        return render_template("msg.html",message="Invalid Login Details")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/admin_logout")
def admin_logout():
    session.clear()
    return render_template("msg.html", message="Logged Out Successfully")


@app.route("/add_staff")
def add_staff():
    staffs = staff_collection.find({})
    staffs = list(staffs)
    return render_template("add_staff.html",staffs=staffs)


@app.route("/add_staff1",methods=['post'])
def add_staff1():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    query = {"username":username}
    count = staff_collection.count_documents(query)
    if count > 0:
        return render_template("msg2.html", message="Duplicate Username")
    query = {"email":email}
    count = staff_collection.count_documents(query)
    if count > 0:
        return render_template("msg2.html",message="Duplicate Email-Id")
    query = {"first_name":first_name, "last_name":last_name, "username":username, "password":password, "email":email}
    staff_collection.insert_one(query)
    return redirect("/add_staff")


@app.route("/add_customer")
def add_customer():
    customers = customer_collection.find({})
    customers = list(customers)
    return render_template("add_customer.html",customers=customers)


@app.route("/add_customer1",methods=['post'])
def add_customer1():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    phone_no = request.form.get("phone_no")
    address1 = request.form.get("address1")
    address2 = request.form.get("address2")
    state = request.form.get("state")
    country = request.form.get("country")
    zipcode = request.form.get("zipcode")
    query = {"username": username}
    count = customer_collection.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Username")
    query = {"email": email}
    count = customer_collection.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Email Address")
    query = {"phone_no": phone_no}
    count = customer_collection.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Phone Number")
    query = {"first_name": first_name, "last_name": last_name, "username": username, "password": password,
             "email": email, "phone_no": phone_no, "address1": address1, "address2": address2, "state": state,
             "country": country, "zipcode": zipcode}
    customer_collection.insert_one(query)
    return redirect("/add_customer")

@app.route("/add_room_type")
def add_room_type():
    room_types = room_type_collection.find({})
    room_types = list(room_types)
    print(room_types)
    return render_template("add_room_type.html",room_types=room_types)


@app.route("/add_rooms")
def add_rooms():
    room_type_id = request.args.get('room_type_id')
    if room_type_id == None:
        query = {}
    else:
        query = {"room_type_id": ObjectId(room_type_id)}
    rooms = room_collection.find(query)
    rooms = list(rooms)
    room_types = room_type_collection.find({})
    room_types = list(room_types)
    return render_template("add_rooms.html",rooms=rooms,room_types=room_types)



@app.route("/add_rooms1", methods=['post'])
def add_rooms1():
    room_type_id = request.form.get("room_type_id")
    rate = request.form.get("rate")
    availability_status = request.form.get("availability_status")
    room_number = request.form.get("room_number")
    description = request.form.get("description")
    number_of_rooms = request.form.get("number_of_rooms")
    query = {"room_number":room_number}
    count = room_collection.count_documents(query)
    if count > 0:
        return render_template("msg.html",message="Duplicate Room Number")
    pic = request.files.get('pic')
    path = PIC_PATH + "/" +pic.filename
    pic.save(path)
    query = {"room_type_id":ObjectId(room_type_id), "rate":rate, "availability_status":availability_status, "room_number":room_number, "description":description, "pic":pic.filename}
    print(query)
    room_collection.insert_one(query)
    query = {"_id": ObjectId(room_type_id)}
    room_type = room_type_collection.find_one(query)
    query2 = {"$set": {"number_of_rooms": int(room_type['number_of_rooms'])+1}}
    room_type_collection.update_one(query, query2)
    return redirect("/add_rooms")


@app.route("/add_room_type1", methods=['post'])
def add_room_type1():
    type = request.form.get("type")
    number_of_rooms = request.form.get("number_of_rooms")
    query = {"type": type, "number_of_rooms":number_of_rooms}
    count = room_type_collection.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Room Type Entry")
    result = room_type_collection.insert_one(query)
    room_type_id = result.inserted_id
    for i in range(1,int(number_of_rooms)+1):
        rate = request.form.get("rate"+str(i))
        room_number = request.form.get("room_number"+str(i))
        description = request.form.get("description"+str(i))
        print(description)
        query = {"room_number": room_number}
        count = room_collection.count_documents(query)
        if count > 0:
            return render_template("msg.html", message="Duplicate Room Number")
        pic = request.files.get('pic'+str(i))
        path = PIC_PATH + "/" + pic.filename
        pic.save(path)
        query = {"room_type_id": ObjectId(room_type_id), "rate": rate, "availability_status": 'Available',
                 "room_number": room_number, "description": description, "pic": pic.filename}
        room_collection.insert_one(query)
    return redirect("/add_room_type")


@app.route("/customer_login")
def customer_login():
    return render_template("customer_login.html")


@app.route("/customer_login_action", methods=['post'])
def customer_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    query = {"username":username, "password":password}
    count = customer_collection.count_documents(query)
    if count > 0:
        customer = customer_collection.find_one(query)
        session['customer_id'] = str(customer['_id'])
        session['role'] = 'customer'
        return redirect("/customer_home")
    else:
        return render_template("msg.html",message="Invalid Login Details")


@app.route("/customer_home")
def customer_home():
    return render_template("customer_home.html")


@app.route("/customer_registration")
def customer_registration():
    return render_template("customer_registration.html")


@app.route("/customer_registration1",methods=['post'])
def customer_registration1():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    phone_no = request.form.get("phone_no")
    address1 = request.form.get("address1")
    address2 = request.form.get("address2")
    state = request.form.get("state")
    country = request.form.get("country")
    zipcode = request.form.get("zipcode")
    query = {"username":username}
    count = customer_collection.count_documents(query)
    if count > 0:
        return render_template("msg.html",message="Duplicate Username")
    query = {"email":email}
    count = customer_collection.count_documents(query)
    if count > 0:
        return render_template("msg.html",message="Duplicate Email Address")
    query = {"phone_no":phone_no}
    count = customer_collection.count_documents(query)
    if count > 0:
        return render_template("msg.html",message="Duplicate Phone Number")
    query = {"first_name":first_name, "last_name":last_name, "username":username, "password":password, "email":email, "phone_no":phone_no, "address1":address1, "address2":address2, "state":state, "country":country, "zipcode":zipcode}
    customer_collection.insert_one(query)
    return render_template("msg.html",message="Registration Completed Successfully")


@app.route("/do_reservation")
def do_reservation():
    room_type_id = request.args.get('room_type_id')
    if room_type_id == None:
        query = {}
    else:
        query = {"room_type_id": ObjectId(room_type_id)}
    room_types = room_type_collection.find({})
    room_types = list(room_types)
    return render_template("do_reservation.html",room_types=room_types)


@app.route("/do_reservation1",methods=['post'])
def do_reservation1():
    expected_check_in_date = request.form.get("expected_check_in_date")
    expected_check_out_date = request.form.get("expected_check_out_date")
    room_type_id = request.form.get('room_type_id')
    expected_check_in_date = expected_check_in_date.replace("T"," ")
    expected_check_out_date = expected_check_out_date.replace("T"," ")
    if room_type_id == "":
       query = {}
    else:
        query = {"room_type_id": ObjectId(room_type_id)}
    rooms = room_collection.find(query)
    rooms = list(rooms)
    print(rooms)
    rooms2 = []
    expected_check_in_date2 = datetime.datetime.strptime(expected_check_in_date, '%Y-%m-%d %H:%M')
    expected_check_out_date2 = datetime.datetime.strptime(expected_check_out_date, '%Y-%m-%d %H:%M')
    for room in rooms:
         query = {"$or": [{"expected_check_in_date": {"$gte": expected_check_in_date2, "$lte": expected_check_out_date2}, "expected_check_out_date": {"$gte": expected_check_in_date2, "$gte": expected_check_out_date2}, "room_id": room['_id'], "reservation_status": {"$ne": "Reservation Cancelled"}},
                  {"expected_check_in_date": { "$lte": expected_check_in_date2, "$lte": expected_check_out_date2}, "expected_check_out_date": {"$gte": expected_check_in_date2, "$lte": expected_check_out_date2}, "room_id": room['_id'], "reservation_status": {"$ne": "Reservation Cancelled"}},
                  {"expected_check_in_date": {"$lte": expected_check_in_date2, "$lte": expected_check_out_date2}, "expected_check_out_date": {"$gte": expected_check_in_date2, "$gte": expected_check_out_date2}, "room_id": room['_id'], "reservation_status": {"$ne": "Reservation Cancelled"}},
                  {"expected_check_in_date": {"$gte": expected_check_in_date2, "$lte": expected_check_out_date2}, "expected_check_out_date": {"$gte": expected_check_in_date2, "$lte": expected_check_out_date2 }, "room_id": room['_id'], "reservation_status": {"$ne": "Reservation Cancelled"}}]}
         count = reservations_collection.count_documents(query)
         if count == 0:
             rooms2.append(room)
    return render_template("do_reservation1.html",rooms=rooms2, expected_check_in_date=expected_check_in_date, expected_check_out_date=expected_check_out_date)



@app.route("/do_reservation2", methods=['post'])
def do_reservation2():
    room_id = request.form.get("room_id")
    customer_id = session['customer_id']
    room_id = request.form.get("room_id")
    query = {"_id":ObjectId(room_id)}
    room = room_collection.find_one(query)
    expected_check_in_date = request.form.get("expected_check_in_date")
    expected_check_out_date = request.form.get("expected_check_out_date")
    expected_check_in_date = datetime.datetime.strptime(expected_check_in_date, '%Y-%m-%d %H:%M')
    expected_check_out_date = datetime.datetime.strptime(expected_check_out_date, '%Y-%m-%d %H:%M')
    diff = expected_check_out_date - expected_check_in_date
    hours = diff.total_seconds() / 3600
    days = hours / 24
    if hours % 24 > 0:
        days = days + 1
    days = int(days)
    total_price = days * int(room['rate'])
    query = {"expected_check_in_date":expected_check_in_date, "expected_check_out_date":expected_check_out_date,"room_id":ObjectId(room_id),"total_price":total_price,"customer_id":ObjectId(customer_id),"reservation_status":"Reserved","payment_status":"Payment Pending"}
    result = reservations_collection.insert_one(query)
    reservation_id = result.inserted_id
    query = {"_id":reservation_id}
    reservations = reservations_collection.find_one(query)
    return render_template("do_reservation2.html",total_price=total_price, reservations=reservations)


@app.route("/do_reservation3", methods=['post'])
def do_reservation3():
    card_type = request.form.get("card_type")
    card_number = request.form.get("card_number")
    name_on_card = request.form.get("name_on_card")
    card_expire_date = request.form.get("card_expire_date")
    card_billing_address = request.form.get("card_billing_address")
    card_billing_postal_code = request.form.get("card_billing_postal_code")
    payment_status = request.form.get("payment_status")
    payment_date = datetime.datetime.now()
    total_amount_paid = request.form.get("total_price")
    customer_id = session['customer_id']
    reservation_id = request.form.get("reservation_id")
    query1 = {"_id":ObjectId(reservation_id)}
    query2 = {"$set":{"payment_status":payment_status}}
    reservations_collection.update_one(query1,query2)
    query = {"payment_date":payment_date,"card_type":card_type,"card_number":card_number,"name_on_card":name_on_card,"card_expire_date":card_expire_date,"card_billing_address":card_billing_address,"card_billing_postal_code":card_billing_postal_code, "total_amount_paid":total_amount_paid,"customer_id":ObjectId(customer_id),"reservation_id":ObjectId(reservation_id),"payment_status":payment_status}
    payment_transactions_collection.insert_one(query)

    return render_template("msg2.html", message="Your Room Reserved Successfully")


@app.route("/pay_later",methods=['post'])
def pay_later():
    reservation_id = request.form.get("reservation_id")
    query1 = {"_id": ObjectId(reservation_id)}
    query2 = {"$set": {"reservation_status": "Reserved"}}
    reservations_collection.update_one(query1,query2)
    return render_template("msg2.html", message="Your Room Reserved Successfully")


@app.route("/view_reservations")
def view_reservations():
    if session['role'] == 'customer':
        customer_id = session['customer_id']
        query = {"customer_id":ObjectId(customer_id)}
    else:
         type = request.args.get("type")
         if type== 'upcoming':
             query = {"reservation_status":"Reserved"}
         elif type == 'current':
             query = {"reservation_status":"Checked In"}
         else:
             query = {"$or":[{"reservation_status":"Checked Out"},{"reservation_status":"Reservation Cancelled"}]}
    reservations = reservations_collection.find(query)
    reservations = list(reservations)
    return render_template("view_reservations.html",reservations=reservations,get_room_by_room_id=get_room_by_room_id,get_customer_by_customer_id=get_customer_by_customer_id)


@app.route("/payment_transactions",methods=['post'])
def payment_transactions():
    reservation_id = request.form.get("reservation_id")
    query = {"reservation_id":ObjectId(reservation_id)}
    payment_transaction = payment_transactions_collection.find_one(query)
    return render_template("payment_transactions.html",payment_transaction=payment_transaction)


@app.route("/up_view_reservations",methods=['post'])
def up_view_reservations():
    reservation_id = request.form.get("reservation_id")
    query1 = {"_id":ObjectId(reservation_id)}
    reservation = reservations_collection.find_one(query1)
    if reservation["payment_status"] != "Payment Pending":
        query2 = {"$set":{"reservation_status":"Reservation Cancelled", "payment_status":"Payment Refunded"}}
    else:
        query2 = {"$set": {"reservation_status": "Reservation Cancelled"}}
    reservations_collection.update_one(query1,query2)
    query = {"reservation_id": ObjectId(reservation_id)}
    query2 = {"$set": {"payment_status":"Payment Refunded"}}
    payment_transactions_collection.update_one(query, query2)

    return render_template("msg2.html",message="Reservation Cancelled")
def get_room_by_room_id(room_id):
    query={"_id":ObjectId(room_id)}
    room = room_collection.find_one(query)
    return room


def get_customer_by_customer_id(customer_id):
    query = {"_id":ObjectId(customer_id)}
    customer = customer_collection.find_one(query)
    return customer


@app.route("/pay",methods=['post'])
def pay():
    reservation_id = request.form.get("reservation_id")
    total_price = request.form.get("total_price")
    return render_template("pay.html", total_price=total_price,reservation_id=reservation_id)


@app.route("/pay1",methods=['post'])
def pay1():
    reservation_id = request.form.get("reservation_id")
    card_type = request.form.get("card_type")
    card_number = request.form.get("card_number")
    name_on_card = request.form.get("name_on_card")
    card_expire_date = request.form.get("card_expire_date")
    card_billing_address = request.form.get("card_billing_address")
    card_billing_postal_code = request.form.get("card_billing_postal_code")
    payment_date = datetime.datetime.now()
    total_price = request.form.get("total_price")
    query1 = {"_id": ObjectId(reservation_id)}
    query2 = {"$set": {"reservation_status": "Reserved"}}
    reservations_collection.update_one(query1, query2)
    query2 = {"$set": {"payment_status": "Success"}}
    reservations_collection.update_one(query1, query2)
    query = {"reservation_id":ObjectId(reservation_id),"payment_date":payment_date,"card_type":card_type,"card_number":card_number,"name_on_card":name_on_card,"card_expire_date":card_expire_date,"card_billing_address":card_billing_address,"card_billing_postal_code":card_billing_postal_code,"total_amount_paid":total_price,"payment_status": "Success"}
    payment_transactions_collection.insert_one(query)

    return render_template("msg2.html",message="Your Room Reserved Successfully")


@app.route("/staff_view_reservations", methods=['post'])
def staff_view_reservations():
    reservation_id = request.form.get("reservation_id")
    query1 = {"_id":ObjectId(reservation_id)}
    query2 = {"$set":{"reservation_status":"Checked In"}}
    reservations_collection.update_one(query1,query2)
    return render_template("msg2.html",message="Checked In Successful")


@app.route("/check_out", methods=['post'])
def check_out():
    reservation_id = request.form.get("reservation_id")
    additional_charge = request.form.get("additional_charge")
    query1 = {"_id":ObjectId(reservation_id)}
    query2 = {"$set":{"reservation_status":"Checked Out"}}
    reservations_collection.update_one(query1,query2)
    query2 = {"$set":{"additional_charge":additional_charge}}
    reservations_collection.update_one(query1,query2)
    return render_template("msg2.html",message="Checked Out Successful")


@app.route("/customer_logout")
def customer_logout():
    session.clear()
    return render_template("msg.html",message="You Have Logged Out Successfully")


@app.route("/staff_login")
def staff_login():
    return render_template("staff_login.html")


@app.route("/staff_login_action", methods=['post'])
def staff_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    query = {"username":username, "password":password}
    count = staff_collection.count_documents(query)
    if count > 0:
        staff = staff_collection.find_one(query)
        session['staff_id'] = str(staff['_id'])
        session['role'] = 'staff'
        return redirect("/staff_home")
    else:
        return render_template("msg.html", message="Invalid Login Details")


@app.route("/staff_home")
def staff_home():
    return render_template("staff_home.html")


@app.route("/collect_cash",methods=['post'])
def collect_cash():
    reservation_id = request.form.get("reservation_id")
    query1 = {"_id":ObjectId(reservation_id)}
    query2 = {"$set":{"payment_status":"Cash Collected"}}
    reservations_collection.update_one(query1,query2)
    query1 = {"reservation_id":ObjectId(reservation_id)}
    payment_transactions_collection.update_one(query1,query2)
    return render_template("msg2.html",message="Cash Collected Successfully")


@app.route("/staff_logout")
def staff_logout():
    session.clear()
    return render_template("msg.html",message="You Have Logged Out Successfully")

app.run(debug=True)