from enum import member

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.sites import requests
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from requests.auth import HTTPBasicAuth

from New_Church_Project.settings import MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET
from main.app_forms import MemberForm, DepositForm, LoginForm, MemberRegistrationForm
from main.models import Member, Project, Transaction, Deposit


# Create your views here.

# def landing_page(request):
#     return None


# @login_required
# def dashboard(request):
#     member = request.user  # Access the logged-in member's profile
#     deposits = member.deposits.all()  # Fetch member's transactions
#     return render(request, 'dashboard.html', {'member': member, 'deposit': deposit})

@login_required
def dashboard(request):
    member = request.user  # Access the logged-in member's profile
    return render(request, 'dashboard.html')


@login_required
def members(request):
    data = Member.objects.all().order_by('id').values()  # ORM select * from members
    paginator = Paginator(data, 15)
    page = request.GET.get('page', 1)
    try:
        paginated_data = paginator.page(page)
    except  EmptyPage:
        paginated_data = paginator.page(1)
    return render(request, "members.html", {"data": paginated_data})


@login_required
@permission_required('main.delete_member', raise_exception=True)
def delete_member(request, member_id):
    member = Member.objects.get(id=member_id)
    member.delete()
    messages.info(request, f"Member {member.first_name} was deleted!!")

    return redirect('members')


@login_required
@permission_required('main.add_customer', raise_exception=True)
def add_member(request):
    if request.method == "POST":
        form = Member(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"Member {form.cleaned_data['first_name']} was added!")
            return redirect('members')
    else:
        form = MemberForm()
    return render(request, 'member_reg.html', {"form": form})


@login_required
@permission_required('main.add_deposit', raise_exception=True)
def deposit(request, member_id, deposits=None):
    member = get_object_or_404(Member, id=member_id)
    if request.method == "POST":
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            deposit_type = form.cleaned_data['deposits']
            deposits = Deposit(amount=amount, status=True, member=member, deposit_type=deposit_type)
            deposits.save()
            messages.success(request, 'Your deposit has been successfully saved')
            return redirect('member_details', member_id=member_id)
    else:
        form = DepositForm()
    return render(request, 'deposit_form.html', {"form": form, "member": member,'deposits': deposits})


@login_required
@permission_required('main.member_details', raise_exception=True)
def member_details(request, member_id):
    member = Member.objects.get(id=member_id)
    deposits = member.deposits.all()
    total = Deposit.objects.filter(member=member).filter(status=True).aggregate(Sum('amount'))['amount__sum']
    return render(request, 'profile.html', {'member': member, 'deposits': deposits, 'total': total})



def register(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            member = form.save()  # Save the form to the database
            messages.success(request, f"Member {member.first_name} was added!")
            return redirect('login')  # Redirect to the members page after adding
        else:
            messages.warning(request, "Member could not be added! Please check the form for errors.")
    else:
        form = MemberRegistrationForm()

    return render(request, 'member_reg.html', {'form': form})



@login_required
def profile_view(request):
    member = get_object_or_404(Member, user=request.user)
    total = Deposit.objects.filter(member=member).filter(status=True).aggregate(Sum('amount'))['amount__sum']
    personal_deposits = Transaction.objects.filter(member=member, transaction_type='deposit')

    context = {
        'member': member,
        'personal_deposits': personal_deposits,
        'total': total
    }

    return render(request, 'profile.html', context)



@login_required
@permission_required('app_name.permission_name', raise_exception=True)
def update_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == "POST":
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f"Member {form.cleaned_data['first_name']} was updated!")
            return redirect('member_details', member_id=member_id)
    else:
        form = MemberForm(instance=member)
    return render(request, 'update_profile.html', {"form": form})


# def search_member(request):
#     return None
#
@csrf_exempt
def callback(request):
    # resp = json.loads(request.body)
    # data = resp['Body']['stkCallback']
    # if data["ResultCode"] == "0":
    #     m_id = data["MerchantRequestID"]
    #     c_id = data["CheckoutRequestID"]
    #     code = ""
    #     amount = ""
    #     item = data["CallbackMetadata"]["Item"]
    #     for i in item:
    #         name = i["Name"]
    #         if name == "MpesaReceiptNumber":
    #             code = i["Value"]
    #
    #         if name == "Amount":
    #             amount = i["Value"]
    #
    #     transaction = Transaction.objects.create(merchant_request_id=m_id, checkout_request_id=c_id, )
    #     transaction.code = code
    #     transaction.amount = amount
    #     transaction.status = 'COMPLETED'
    #     transaction.save()
    # return HttpResponse("OK")
    return render(request, 'transactions.html')


@login_required
def pie_chart(request):
    deposits = Deposit.objects.all()
    grouped = deposits.values('deposit_type').annotate(count=Count('id'))

    labels = [item['deposit_type'] for item in grouped]
    counts = [item['count'] for item in grouped]

    return JsonResponse({
        "title": "Deposits Grouped by Type",
        "data": {
            "labels": labels,
            "datasets": [{
                "data": counts,
                "backgroundColor": ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796', '#2e59d9'],
                "hoverBackgroundColor": ['#2e59d9', '#17a673', '#2c9faf', '#d4aa33', '#be3a2d', '#6e707e', '#1d4ca7'],
                "hoverBorderColor": "rgba(234, 236, 244, 1)",
            }],
        },
    })


@login_required
def line_chart(request):
    deposits = Deposit.objects.all()
    grouped = deposits.annotate(month=TruncMonth('created_at')).values('month').annotate(
        total=Count('id')).order_by('month')

    numbers = [item['total'] for item in grouped]
    months = [item['month'].strftime('%b') for item in grouped]

    return JsonResponse({
        "title": "Deposits Over Time",
        "data": {
            "labels": months,
            "datasets": [{
                "label": "Total Deposits",
                "lineTension": 0.3,
                "backgroundColor": "rgba(78, 115, 223, 0.05)",
                "borderColor": "rgba(78, 115, 223, 1)",
                "pointRadius": 3,
                "pointBackgroundColor": "rgba(78, 115, 223, 1)",
                "pointBorderColor": "rgba(78, 115, 223, 1)",
                "pointHoverRadius": 3,
                "pointHoverBackgroundColor": "rgba(78, 115, 223, 1)",
                "pointHoverBorderColor": "rgba(78, 115, 223, 1)",
                "pointHitRadius": 10,
                "pointBorderWidth": 2,
                "data": numbers,
            }],
        }
    })


@login_required
def bar_chart(request):
    deposits = Deposit.objects.all()
    complete = deposits.filter(status=True).count()
    pending = deposits.filter(status=False).count()

    return JsonResponse({
        "title": "Deposits Grouped by Status",
        "data": {
            "labels": ["Complete", "Pending"],
            "datasets": [{
                "label": "Deposits",
                "backgroundColor": ["#4e73df", "#e74a3b"],
                "hoverBackgroundColor": ["#2e59d9", "#be3a2d"],
                "borderColor": "#4e73df",
                "data": [complete, pending],
            }],
        },
    })


def login_page(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {"form": form})
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)  # sessions # cookies
                return redirect('members')
        messages.error(request, "Invalid username or password")
        return render(request, "login.html", {"form": form})


@login_required()
def logout_page(request):
    logout(request)
    return redirect('login')


# @login_required
# def profile(request, member_id):
#     member = request.user.member if hasattr(request.user, 'member') else None
#
#     if member and member.id:  # Ensure member and its ID exist
#         profile_url = reverse('profile', kwargs={'member_id': member.id})
#     else:
#         profile_url = None  # No profile available for this user
#
#     return render(request, 'profile.html', {'profile_url': profile_url})


@login_required
def church_projects(request):
    status = request.GET.get('status', None)
    if status:
        projects = Project.objects.filter(status=status)
    else:
        projects = Project.objects.all()
    return render(request, 'church_projects.html', {'projects': projects})


# def project(request):
#     return None
@login_required
@permission_required('main.add_member', raise_exception=True)
def member_reg(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST, request.FILES)  # Include request.FILES for file uploads
        if form.is_valid():
            member = form.save()  # Save the form to the database
            messages.success(request, f"Member {member.first_name} was added!")
            return redirect('members')  # Redirect to the members page after adding
        else:
            messages.warning(request, "Member could not be added! Please check the form for errors.")
    else:
        form = MemberRegistrationForm()

    return render(request, 'member_form.html', {'form': form})


@login_required
def personal_deposit(request):
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            member = get_object_or_404(Member, user=request.user)

            # Trigger M-Pesa Payment
            mpesa_response = initiate_mpesa_payment(request.user.phone_number, amount)  # Adjust logic here
            if mpesa_response.get('success'):
                # Save transaction after successful M-Pesa payment
                Transaction.objects.create(
                    member=member,
                    amount=amount,
                    transaction_type='deposit',
                )
                return JsonResponse({'success': True, 'message': 'Deposit successful!'})
            else:
                return JsonResponse({'success': False, 'message': 'M-Pesa payment failed. Try again later.'})
    else:
        form = DepositForm()
    return render(request, 'deposit_form.html', {'form': form})

def get_mpesa_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    return response.json().get('access_token')

def initiate_mpesa_payment(phone_number, amount):
    access_token = get_mpesa_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "BusinessShortCode": '',
        "Password": '',  # Generate Password Dynamically
        "Timestamp": "20250117202530",  # Use a proper timestamp
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB":'',
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/mpesa/callback",
        "AccountReference": "Church Deposit",
        "TransactionDesc": "Church Contribution",
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()
