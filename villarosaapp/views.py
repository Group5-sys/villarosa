import json

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from requests.auth import HTTPBasicAuth

from villarosaapp.credentials import MpesaAccessToken, LipanaMpesaPpassword
from villarosaapp.models import *

from villarosaapp.models import Bookings


# Create your views here.
def index(request):
    return render(request, 'index.html')

def starter(request):
    return render(request, 'starter-page.html')

def about(request):
    return render(request, 'about.html')

def chefs(request):
    return render(request, 'chefs.html')

def gallery(request):
    return render(request, 'gallery.html')

def menu(request):
    return render(request, 'menu.html')

def specials(request):
    return render(request, 'specials.html')

def events(request):
    return render(request, 'events.html')

def contact(request):
    if request.method == "POST":
        mycontact = Contact(

            name=request.POST['name'],
            email=request.POST['email'],
            subject=request.POST['subject'],
            message=request.POST['message'],
        )
        mycontact.save()
        return redirect('contact')

    else:
        return render(request,'contact.html')

@login_required
def book(request):
    if request.method == "POST":
        mybooking = Bookings(
            user=request.user,  # Associate booking with the logged-in user
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            date=request.POST['date'],
            time=request.POST['time'],
            people=request.POST['people'],
            message=request.POST['message'],
        )
        mybooking.save()
        return redirect('pay')  # Redirect after booking

    return render(request, 'book.html')




@login_required
def reservations(request):
    user_bookings = Bookings.objects.filter(user=request.user)  # Show only the user's bookings
    return render(request, 'reservations.html', {'all': user_bookings})

@login_required
def edit(request, id):
    booking = get_object_or_404(Bookings, id=id, user=request.user)  # Ensure user owns the booking
    if request.method == 'POST':
        booking.name = request.POST.get('name')
        booking.email = request.POST.get('email')
        booking.phone = request.POST.get('phone')
        booking.date = request.POST.get('date')
        booking.time = request.POST.get('time')
        booking.people = request.POST.get('people')
        booking.message = request.POST.get('message')
        booking.save()
        return redirect('/admindashboard')
    return render(request, 'edit.html', {'booking': booking})

@login_required
def delete(request, id):
    booking = get_object_or_404(Bookings, id=id, user=request.user)  # Restrict deletion
    booking.delete()
    return redirect('/book')

#mpesa api--------

def token(request):
    consumer_key = '77bgGpmlOxlgJu6oEXhEgUgnu0j2WYxA'
    consumer_secret = 'viM8ejHgtEmtPTHd'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'token.html', {"token":validated_mpesa_access_token})

def pay(request):
   return render(request, 'pay.html')


def stk(request):
    if request.method == "POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request_data = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/callback",
            "AccountReference": "Medilab",
            "TransactionDesc": "Appointment"
        }
        response = requests.post(api_url, json=request_data, headers=headers)

        response_data = response.json()
        transaction_id = response_data.get("CheckoutRequestID", "N/A")
        result_code = response_data.get("ResponseCode", "1")  # 0 is success, 1 is failure

        if result_code == "0":
            # Only save transaction if it was successful
            transaction = Transaction(
                phone_number=phone,
                amount=amount,
                transaction_id=transaction_id,
                status="Success"
            )
            transaction.save()

            return HttpResponse(f"Transaction ID: {transaction_id}, Status: Success")
        else:
            return HttpResponse(f"Transaction Failed. Error Code: {result_code}")




def transactions_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    return render(request, 'transaction.html', {'transactions': transactions})


def register(request):
    """ Show the registration form """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Check the password
        if password == confirm_password:
            try:
                user = User.objects.create_user(username=username, password=password)
                user.save()

                # Display a message
                messages.success(request, "Account created successfully")
                return redirect('/login')
            except:
                # Display a message if the above fails
                messages.error(request, "Username already exist")
        else:
            # Display a message saying passwords don't match
            messages.error(request, "Passwords do not match")

    return render(request, 'register.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        # Check if the user exists
        if user is not None:
            # login(request, user)
            login(request,user)
            messages.success(request, "You are now logged in!")
            return redirect('/home')
        else:
            messages.error(request, "Invalid login credentials")

    return render(request, 'login.html')


def admin_login_view(request):
    # Admin credentials
    admin_username = "ayala"
    admin_email = "inno.innocent.cent@gmail.com"
    admin_password = "@Taty1234$"

    # Ensure admin user exists
    if not User.objects.filter(username=admin_username).exists():
        User.objects.create_superuser(username=admin_username, email=admin_email, password=admin_password)
        print("Superuser created successfully!")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.username == admin_username:
            login(request, user)
            messages.success(request, "Welcome Admin!")
            return redirect('/admindashboard')  # Redirect to transactions page
        else:
            messages.error(request, "Invalid credentials! Only admin can log in.")
            return redirect('/adminlogin')  # Redirect back to login page

    return render(request, 'adminlogin.html')



def admindashboard(request):
    all1 = Bookings.objects.all()
    return render(request,'admindashboard.html',{'all1': all1})


