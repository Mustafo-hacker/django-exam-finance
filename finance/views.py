from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.db.models import Sum
from decimal import Decimal

from .models import Transaction, Profile



def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    transactions = Transaction.objects.filter(user=request.user)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    total_income = transactions.filter(type="income").aggregate(Sum("amount"))["amount__sum"] or Decimal('0')
    total_expense = transactions.filter(type="expense").aggregate(Sum("amount"))["amount__sum"] or Decimal('0')

    from_amount = request.GET.get('from_amount')
    to_amount = request.GET.get('to_amount')
    category_search = request.GET.get('category_search') 

    filtered_transactions = transactions

    if from_amount:
        filtered_transactions = filtered_transactions.filter(amount__gte=Decimal(from_amount))
    if to_amount:
        filtered_transactions = filtered_transactions.filter(amount__lte=Decimal(to_amount))
    if category_search:
        filtered_transactions = filtered_transactions.filter(category__icontains=category_search)

    return render(request, 'home.html', {
        'transactions': filtered_transactions,
        'balance': profile.balance,
        'total_income': total_income,
        'total_expense': total_expense,
        'from_amount': from_amount or '',
        'to_amount': to_amount or '',
        'category_search': category_search or ''
    })




def delete_user(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    transaction = get_object_or_404(Transaction, id=pk, user=request.user)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if transaction.type == "income":
        profile.balance -= transaction.amount
    else:
        profile.balance += transaction.amount

    profile.save()
    transaction.delete()
    return redirect('home')


def add_transaction(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))
        type_ = request.POST.get('type')
        category = request.POST.get('category')
        description = request.POST.get('description')

        t = Transaction.objects.create(
            user=request.user,
            amount=amount,
            type=type_,
            category=category,
            description=description
        )

        profile, _ = Profile.objects.get_or_create(user=request.user)
        if type_ == "income":
            profile.balance += amount
        else:
            profile.balance -= amount
        profile.save()

        return redirect('home')

    return render(request, 'add_transaction.html')


def edit_transaction(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    transaction = get_object_or_404(Transaction, id=pk, user=request.user)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if transaction.type == "income":
            profile.balance -= transaction.amount
        else:
            profile.balance += transaction.amount

        new_amount = Decimal(request.POST.get('amount'))
        new_type = request.POST.get('type')
        new_category = request.POST.get('category')
        new_description = request.POST.get('description')

        transaction.amount = new_amount
        transaction.type = new_type
        transaction.category = new_category
        transaction.description = new_description
        transaction.save()

        if new_type == "income":
            profile.balance += new_amount
        else:
            profile.balance -= new_amount

        profile.save()

        return redirect('home')

    return render(request, 'edit_transaction.html', {'transaction': transaction})


def edit_balance(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        new_balance = Decimal(request.POST.get("balance"))
        profile.balance = new_balance
        profile.save()
        return redirect("home")

    return render(request, "edit_balance.html", {"profile": profile})
