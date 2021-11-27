from django.shortcuts import render, redirect
from product import models as ProductModels
from cart import models as CartModels
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
""" User Models """
from django.contrib.auth.models import User
from user_profile import models as UserProfileModels


def customerLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        """ Authenticate method will perfrom a match with submitted data and database """
        user = authenticate(request, username=username, password=password)
        if user is not None:
            """ Login method make user authorized """
            login(request, user)

            """ redirect will take url pattern name """
            return redirect('homePage')
        else:
            """ User can see this messages with defined tages in setting.py file """
            messages.error(request, 'Invlid Crendtials, or account suspended')
            return redirect('customerLogin')
    else:
        navigationProductCategories = ProductModels.ProductCategory.objects.filter(
            status=True).order_by('-id')[:4]
        return render(request, 'customer-login.html', {
            'navigationProductCategories': navigationProductCategories,
        })


def customerLogout(request):
    logout(request)
    return redirect('homePage')


def CustomerRegistration(request):
    """ Customer Registration Function with GET and POST handler """
    if request.method == 'POST':
        firstName = request.POST.get('first_name')
        lastName = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirm_password')

        """check username is already available in database or not"""
        checkUsername = User.objects.filter(username=username).exists()
        if checkUsername == False:
            """ get user object and create user """
            if password == confirmPassword:
                user = User.objects.create(
                    first_name=firstName,
                    last_name=lastName,
                    username=username
                )
                """ Encrypt password """
                user.set_password(password)
                user.save()
                messages.success(
                    request, 'Thank You for registration you can login to your account')
                return redirect('customerLogin')
            else:
                messages.error(
                    request, 'Password does not match with confirm password')
                return redirect('CustomerRegistration')
        else:
            messages.error(request, 'Username is already taken')
            return redirect('CustomerRegistration')
    else:
        navigationProductCategories = ProductModels.ProductCategory.objects.filter(
            status=True).order_by('-id')[:4]
        return render(request, 'customer-registration.html', {
            'navigationProductCategories': navigationProductCategories
        })


def homePage(request):
    """ Fetch latest data in acending order by id """
    navigationProductCategories = ProductModels.ProductCategory.objects.filter(
        status=True).order_by('-id')[:4]
    productCategories = ProductModels.ProductCategory.objects.filter(
        status=True)
    products = ProductModels.Product.objects.filter(
        status=True).order_by('-id')[:4]

    return render(request, 'index.html', {
        'navigationProductCategories': navigationProductCategories,
        'productCategories': productCategories,
        'products': products
    })


def CategoryProducts(request, product_category_id):
    """ Product list according to category"""
    navigationProductCategories = ProductModels.ProductCategory.objects.filter(
        status=True).order_by('-id')[:4]
    products = ProductModels.Product.objects.filter(
        product_category_id=product_category_id)
    productCategories = ProductModels.ProductCategory.objects.filter(
        status=True)
    return render(request, 'category-product.html', {
        'navigationProductCategories': navigationProductCategories,
        'products': products,
        'productCategories': productCategories
    })


def ProductDetails(request, product_id):
    navigationProductCategories = ProductModels.ProductCategory.objects.filter(
        status=True).order_by('-id')[:4]
    try:
        product = ProductModels.Product.objects.get(id=product_id)
    except ProductModels.Product.DoesNotExist:
        product = {}

    return render(request, 'product-details.html', {
        'navigationProductCategories': navigationProductCategories,
        'product': product
    })


def AddToCart(request, product_id):
    """ Add Product to cart """
    if request.user.is_authenticated:
        """  get_or_create either create object if not exist or fetch object if exist """
        cart, _ = CartModels.Cart.objects.get_or_create(
            product_id=product_id, user=request.user)
        messages.success(request, 'Your Product has been added to cart')
    return redirect('ProductDetails', product_id=product_id)


def CustomerCart(request):
    """ Customer Cart Page """
    if request.user.is_authenticated:
        navigationProductCategories = ProductModels.ProductCategory.objects.filter(
            status=True).order_by('-id')[:4]
        carts = CartModels.Cart.objects.filter(user=request.user)
        return render(request, 'customer-cart.html', {
            'navigationProductCategories': navigationProductCategories,
            'carts': carts
        })
    else:
        return redirect('customerLogin')


def DeleteCartProduct(request, cart_id):

         if request.user.is_authenticated:
                try:
                    CartModels.Cart.objects.get(id=cart_id).delete()
                except CartModels.Cart.DoesNotExist:
                    pass
                messages.success(request, 'Product deleted form cart')
                return redirect('CustomerCart')
         else:
                return redirect('customerLogin')


def CustomerProfile(request):
   if request.user.is_authenticated:
        userProfile, _ = UserProfileModels.UserProfile.objects.get_or_create(
            user=request.user)
        if request.method == 'POST':
            firstName = request.POST.get('first_name')
            lastName = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirmPassword = request.POST.get('confirm_password')
            address = request.POST.get('address')
            mobile = request.POST.get('mobile')
            profilePicture = request.FILES.get('profile_picture')

            request.user.first_name = firstName
            request.user.last_name = lastName
            request.user.email = email
            request.user.save()
            userProfile.address = address
            userProfile.mobile = mobile

            if profilePicture:
                userProfile.profile_picture = profilePicture
            userProfile.save()

            if password != "":
                if confirmPassword == "":
                    messages.error(request, 'Please Enter confirm password')
                    return redirect('CustomerProfile')
                if password == confirmPassword:
                    request.user.set_password(password)
                    request.user.save()
                    messages.error(request, 'Password updated successfuly')
                    return redirect('customerLogin')
                else:
                    messages.error(
                        request, 'Password does not match with confirm password')
                    return redirect('CustomerProfile')

            messages.success(request, 'Profile updated successfully')
            return redirect('CustomerProfile')

        else:
            navigationProductCategories = ProductModels.ProductCategory.objects.filter(
                status=True).order_by('-id')[:4]
            return render(request, 'customer-profile.html', {
                'navigationProductCategories': navigationProductCategories,
                'userProfile': userProfile,
            })
   else:
        return redirect('homePage')