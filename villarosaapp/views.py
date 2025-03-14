import json

import requests


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
            return redirect('reservations')
        else:
            return render(request,'contact.html'),


def book(request):
    if request.method == "POST":
       mybooking =Bookings(
            name=request.POST['name'],
            email=request.POST['email'],
            phone=request.POST['phone'],
            date=request.POST['date'],
            time=request.POST['time'],
            people=request.POST['people'],
            message = request.POST['message'],

       )
       mybooking.save()
       return redirect('reservations')

    else:
        return render(request,'book.html' )




def reservations(request):
    all = (
        Bookings.objects.all())
    return render(request,'reservations.html',{'all':all})


def delete(request,id):
    deletebooking = Bookings.objects.get(id=id)
    deletebooking.delete()
    return redirect('/reservations')

def edit(request,id):
    bookings = get_object_or_404 (Bookings, id=id)
    if request.method == 'POST':
        bookings.name = request.POST.get('name')
        bookings.email = request.POST.get('email')
        bookings.phone = request.POST.get('phone')
        bookings.date = request.POST.get('date')
        bookings.time = request.POST.get('time')
        bookings.people = request.POST.get('people')
        bookings.message = request.POST.get('message')
        bookings.save()
        return redirect('/reservations')
    else:
        return render(request, 'edit.html', {'booking': bookings})


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
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "Medlab",
            "TransactionDesc": "Appointment Charges"
        }
        response = requests.post(api_url, json=request_data, headers=headers)

        # Parse response
        response_data = response.json()
        transaction_id = response_data.get("CheckoutRequestID", "N/A")
        result_code = response_data.get("ResponseCode", "1")  # 0 is success, 1 is failure

        # Save transaction to database
        transaction = Transaction(
            phone_number=phone,
            amount=amount,
            transaction_id=transaction_id,
            status="Success" if result_code == "0" else "Failed"
        )
        transaction.save()

        return HttpResponse(
            f"Transaction ID: {transaction_id}, Status: {'Success' if result_code == '0' else 'Failed'}")


def transactions_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    return render(request, 'transactions.html', {'transactions': transactions})



