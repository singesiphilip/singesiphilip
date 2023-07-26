from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q 
from .forms import *
from .models import *
from userprofile.models import *
import uuid
import json
import requests

# Create your views here.

def home(request):
    top = Product.objects.filter(topselling=True)
    feature = Product.objects.filter(featured=True)
    
   

    context = {
        'top': top,
        'feature': feature,
   
      }

    return render(request,'index.html', context)

def products(request):
    allprod = Product.objects.all()
    p = Paginator(allprod, 8)
    page = request.GET.get('page')
    pagin = p.get_page(page)

    context = {
        'pagin': pagin,
        
    }
    return render(request, 'products.html', context)

def detail(request, id):
    prodet = Product.objects.get(pk = id) 

    context = {
        'prodet':prodet,
    }

    return render(request, 'detail.html', context)

def category(request, id, slug):
    catname = Category.objects.get(pk=id)
    catprod = Product.objects.filter(Category_id = id)

    context = {
        'catname': catname,
        'catprod': catprod,
    }
    return render(request, 'category.html', context)


def contact(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'your message has been sent')
            return redirect('home')
        else:
            messages.error(request, 'please enter a valid information')
            return redirect('contact')

    context = {
        'form': form,
    }       

    return render(request, 'contact.html' ,context)


def signout(request):
    logout(request)
    messages.success(request, 'you are now signed out')
    return redirect('home')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('home')
        else:
            messages.info(request, 'username/password incorrect')
            return redirect('signin')
        
    return render(request, 'login.html')

def register(request):
    customer = CustomerForm()
    if request.method == 'POST':
        phone = request.POST['phone']
        address = request.POST['address']
        pix = request.POST['pix']
        customer = CustomerForm(request.POST)
        if customer.is_valid():
            user = customer. save()
            newuser = Customer()
            newuser.user = user
            newuser.first_name = user.first_name
            newuser.last_name = user.last_name
            newuser.email = user.email
            newuser.phone = phone
            newuser.address = address
            newuser.pix = pix
            newuser.save()
            messages.success(request, f'dear {user} your account has been created successfully')
            return redirect('signin')
        else:
            messages.error(request, customer.errors)
            return redirect('register')

    return render(request, 'register.html')


@login_required(login_url='signin')
def profile(request):
    userprof = Customer.objects.get(user__username=request.user.username)

    context = {
        'userprof': userprof,
    }

    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def profile_update(request):
    userprof = Customer.objects.get(user__username=request.user.username)
    profile = Profileform(instance=request.user.customer)
    if request.method == 'POST':
        profile = Profileform(request.POST, request.FILES, instance=request.user.customer)
        if profile.is_valid():
            pupdate = profile.save()
            new = pupdate.first_name
            messages.success(request, f'dear {new} your profile update is successful')
            return redirect('profile')
        else:
            messages.error(request, f'your profile update genersted the following errors: {profile.errors}')
            return redirect('profile_update')
        
    context = {
        'userprof':userprof
    }    

    return render(request, 'profile_update.html', context)


@login_required(login_url='signin')
def password_update(request):
    userprof = Customer.objects.get(user__username=request.user.username)
    form = PasswordChangeForm(request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            newpass = form.save()
            update_session_auth_hash(request, form)
            messages.success(request, 'Password change successfully')
            return redirect('profile')
        else:
            messages.error(request, f'the following errors were encountered: {form.errors}')
            return redirect('password_update')

    context = {
        'userprof':userprof,
        'form':form,
    }

    return render(request, 'password_update.html', context)

@login_required(login_url='signin')
def add_to_cart(request):
    if request.method == 'POST':
        item = request.POST['itemid']
        quantity = int(request.POST['quantity'])
        product = Product.objects.get(id=item)
        if product.promo_price:
            new_price = product.promo_price
        else:
            new_price = product.price
        cart = Cart.objects.filter(user__username = request.user.username, paid=False)
        if cart:
            basket = Cart.objects.filter(user__username=request.user.username, paid=False, product=product.id, quantity=quantity, price = new_price).first()
            if basket:
                basket.quantity += quantity
                basket.amount = basket.quantity * new_price
                basket.save()
                messages.success(request, 'one item added to cart')
                return redirect('home')
            else:
                newitem = Cart()
                newitem.user = request.user
                newitem.product = product
                newitem.quantity = quantity
                newitem.price = new_price
                newitem.amount = new_price * quantity
                newitem.paid =False
                newitem.save()
                messages.success(request, 'one item added to cart')
                return redirect('home')
            
        else:
                newcart = Cart()
                newcart.user = request.user
                newcart.product = product
                newcart.quantity = quantity
                newcart.price = new_price
                newcart.amount = new_price * quantity
                newcart.paid =False
                newcart.save()
                messages.success(request, 'one item added to cart')
                return redirect('home')


@login_required(login_url='signin')        
def cart(request):
    cart = Cart.objects.filter(user__username = request.user.username, paid=False)
    for item in cart:
        item.amount = item.price * item.quantity
        item.save()

    subtotal = 0
    vat = 0 
    total = 0

    for item in cart:
        subtotal += item.amount
        vat = 0.075 * subtotal
        total = subtotal + vat

    context = {
        'cart':cart,
        'subtotal':subtotal,
        'vat':vat,
        'total':total
    }    
    return render(request, 'cart.html', context)      

@login_required(login_url='signin')
def delete(request):
    if request.method == 'POST':
        delid = request.POST['itemid']
        Cart.objects.get(pk=delid).delete()
        messages.success(request, 'one item removed')
        return redirect('cart')  

@login_required(login_url='signin')   
def update(request):
    if request.method == 'POST':
        itemid = request.POST['itemid'] 
        quant = request.POST['quant']
        newquant = Cart.objects.get(pk=itemid)
        newquant.quantity = quant
        newquant.amount = newquant.quantity * newquant.price
        newquant.save()
        messages.success(request, 'quantity updated') 
        return redirect('cart')  

@login_required(login_url='signin')    
def checkout(request):
    userprof = Customer.objects.get(user__username=request.user.username)
    cart = Cart.objects.filter(user__username = request.user.username)
    for item in cart:
        item.amount = item.price * item.quantity
        item.save()

    subtotal = 0
    vat = 0 
    total = 0

    for item in cart:
        subtotal += item.amount
        vat = 0.075 * subtotal
        total = subtotal + vat

    context = {
        'cart':cart,
        'total':total,
        'userprof':userprof  
    }    

    return render(request, 'checkout.html', context)

@login_required(login_url='signin')
def payment(request):
    if request.method == 'POST':
        profile = Customer.objects.get(user__username = request.user.username)
        api_key = 'sk_test_7bb1069f3c8959d922bf742d65e043cf0049bf72' #secret key for paystack
        curl = 'https://api.paystack.co/transaction/initialize' #paystack call url
        cburl = 'http://16.170.247.221/callback' #callback or thank you page
        ref = str(uuid.uuid4()) #reference ID required by paystack as an additional ref number 
        order_no = profile.id
        amount = float(request.POST['total']) * 100 #total amount to be charged
        email = profile.email
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        address = request.POST['address']
        phone = request.POST['phone']

        #Collect data to send to paystack via call url
        headers = {'Authorization': f'Bearer {api_key}'}
        data = {'reference':ref, 'amount':int(amount), 'email':email, 'callback_url':cburl, 'order_number':order_no, 'currency':'NGN'}

        #Make a call to paystack
        try:
            r = requests.post(curl, headers=headers, json=data)
        except Exception:
            messages.error(request, "Network busy, please try again")
        else:
            transback = json.loads(r.text)
            rdurl = transback['data']['authorization_url']  #where you add your card info


            neworder = Order()
            neworder.user = profile.user
            neworder.first_name = first_name
            neworder.last_name = last_name
            neworder.email = email
            neworder.phone = phone
            neworder.address = address
            neworder.pay_code = ref
            neworder.paid = True
            neworder.save()

            return redirect(rdurl)
        
    return redirect('checkout')

@login_required(login_url='signin')
def callback(request):
    userprof = Customer.objects.get(user__username = request.user.username, paid=False)
    cart = Cart.objects.filter(user__username = request.user.username)

    for item in cart:
        item.paid = True
        item.save()


    context = {
        'userprof':userprof,
        'cart':cart
    }    

    return render(request, 'callback.html', context)


def search(request):
    if request.method == 'POST':
        item = request.POST["item"]
        search_item = Q(Q(title__icontains = item)|Q(description__contains = item))
        search = Product.objects.filter(search_item)

        context = {
            'search':search,
            'item':item
        }

        return render(request, 'search.html', context)
