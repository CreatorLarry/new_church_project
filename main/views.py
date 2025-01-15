from enum import member

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from main.app_forms import MemberForm, DepositForm, LoginForm, MemberRegistrationForm
from main.models import Member, Project, Transaction, Deposit


# Create your views here.

# def landing_page(request):
#     return None


@login_required
def dashboard(request):
    member = request.member.profile  # Access the logged-in member's profile
    deposits = member.transactions.all()  # Fetch member's transactions
    return render(request, 'dashboard.html', {'member': member, 'deposits': deposits})


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
@permission_required
def delete_member(request):
    def delete_member(request, member_id):
        member = Member.objects.get(id=member_id)
        member.delete()
        messages.info(request, f"Member {member.first_name} was deleted!!")

        return redirect('members')


@login_required
@permission_required
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
@permission_required
def deposit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == "POST":
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            depo = Deposit(amount=amount, status=True, member=member)
            depo.save()
            messages.success(request, 'Your deposit has been successfully saved')
            return redirect('members')
    else:
        form = DepositForm()
    return render(request, 'deposit_form.html', {"form": form, "member": member})


@login_required
@permission_required
def member_details(request, member_id):
    member = Member.objects.get(id=member_id)
    deposits = member.deposits.all()
    total = Deposit.objects.filter(member=member).filter(status=True).aggregate(Sum('amount'))['amount__sum']
    return render(request, 'profile.html', {'member': member, 'deposits': deposits, 'total': total})


def register(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after registration
    else:
        form = MemberRegistrationForm()
    return render(request, 'member_reg.html', {'form': form})


# @login_required
# def profile(request, member_id):
#     member = Member.objects.get(id=member_id)
#     deposits = member.deposits.all()
#     total = Deposit.objects.filter(member=member).filter(status=True).aggregate(Sum('amount'))['amount__sum']
#     return render(request, 'profile.html', {'member': member, 'deposits': deposits, 'total': total})

@login_required
@permission_required
def update_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    if request.method == "POST":
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f"Member {form.cleaned_data['first_name']} was updated!")
            return redirect('members')
    else:
        form = MemberForm(instance=member)
    return render(request, 'update_profile.html', {"form": form})


# def search_member(request):
#     return None
#
@login_required
@permission_required
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
    grouped = deposits.values('deposit_for').annotate(count=Count('id'))

    labels = [item['deposit_for'] for item in grouped]
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


def logout_page(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    member = request.user.member if hasattr(request.user, 'member') else None

    if member and member.id:  # Ensure member and its ID exist
        profile_url = reverse('profile', kwargs={'member_id': member.id})
    else:
        profile_url = None  # No profile available for this user

    return render(request, 'dashboard.html', {'profile_url': profile_url})


@login_required
@permission_required
def church_projects(request):
    status = request.GET.get('status', None)
    if status:
        projects = Project.objects.filter(status=status)
    else:
        projects = Project.objects.all()
    return render(request, 'church_projects.html', {'church_projects': church_projects})
