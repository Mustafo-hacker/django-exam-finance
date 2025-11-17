from django.shortcuts import render, redirect, HttpResponse
from .models import Transaction

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    transactions = Transaction.objects.filter(user=request.user)

    return render(request, 'home.html', {'transactions': transactions})

def delete_user(request,pk):
    if request.user.is_authenticated:
        transactions = Transaction.objects.filter(id=pk).first()
        if not transactions:
            return HttpResponse("404 cannot find user")
        try:
            transactions.delete()
            return redirect('/')
        except Exception as err:
            return HttpResponse(str(err))
        
    return redirect('login')


def add_transaction(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        type_ = request.POST.get('type')  
        category = request.POST.get('category')
        description = request.POST.get('description')

        Transaction.objects.create(
            user=request.user,
            amount=amount,
            type=type_,
            category=category,
            description=description
        )

        return redirect('home') 

    return render(request, 'add_transaction.html')


def edit_transaction(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')

    transaction = Transaction.objects.filter(id=pk, user=request.user).first()
    if not transaction:
        return redirect('home')  

    if request.method == 'POST':
        transaction.amount = request.POST.get('amount')
        transaction.type = request.POST.get('type')
        transaction.category = request.POST.get('category')
        transaction.description = request.POST.get('description')

        transaction.save()

        return redirect('home')  

    return render(request, 'edit_transaction.html', {
        'transaction': transaction
    })
