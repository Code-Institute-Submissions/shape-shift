from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Comment, Rating
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .forms import ContactForm, CommentForm, RatingForm


def all_products(request):
    """ A view to show all products, including sorting and search queries """

    # Start with the default queryset of all products
    products = Product.objects.all()

    # Define default sorting options
    sort = request.GET.get('sort', 'name')  # Default to sorting by name
    direction = request.GET.get('direction', 'asc')  # Default to ascending order

    # Handle sorting based on user input
    if sort == 'name':
        field_to_sort = 'name'
    elif sort == '-name':
        field_to_sort = '-name'  # Adjust the value to match the HTML
    elif sort == 'price':
        field_to_sort = 'price'
    elif sort == '-price':
        field_to_sort = '-price'  # Adjust the value to match the HTML
    else:
        field_to_sort = 'name'  # Default to sorting by name

    # Apply sorting direction
    if direction == 'desc':
        field_to_sort = '-' + field_to_sort  # Add '-' for descending order

    # Apply sorting to the queryset
    products = products.order_by(field_to_sort)

    # Handle search queries
    query = request.GET.get('q', None)
    if query:
        queries = Q(name__icontains=query) | Q(description__icontains=query)
        products = products.filter(queries)

    context = {
        'products': products,
        'search_term': query,
        'sort': sort,
        'direction': direction,
    }

    return render(request, 'store/all_products.html', context)


def women_products(request):
    products = Product.objects.filter(category='Women')
    return render(request, 'clothes/women.html', {'products': products})


def men_product_list(request):  
    products = Product.objects.filter(category='Men')  
    return render(request, 'clothes/men.html', {'products': products})


def keychain_products(request):
    products = Product.objects.filter(category="Keychains")
    return render(request, 'store/keychains.html', {'products': products})


def wriststraps_products(request):
    products = Product.objects.filter(category="Wriststraps")
    return render(request, 'store/wriststraps.html', {'products': products})


def yogamats_products(request):
    products = Product.objects.filter(category="Yogamats")
    return render(request, 'store/yogamats.html', {'products': products})


def foamrollers_products(request):
    products = Product.objects.filter(category="Foamrollers")
    return render(request, 'store/foamrollers.html', {'products': products})


def protein_products(request):
    products = Product.objects.filter(category="Protein")
    return render(request, 'store/protein.html', {'products': products})


def creatine_products(request):
    products = Product.objects.filter(category="Creatine")
    return render(request, 'store/creatine.html', {'products': products})


def electrolytes_products(request):
    products = Product.objects.filter(category="Electrolytes")
    return render(request, 'store/electrolytes.html', {'products': products})


def preworkout_products(request):
    products = Product.objects.filter(category="Preworkout")
    return render(request, 'store/preworkout.html', {'products': products})


def postworkout_products(request):
    products = Product.objects.filter(category="Postworkout")
    return render(request, 'store/postworkout.html', {'products': products})


def add_to_cart(request, product_id):
    # Retrieve the product based on the product_id
    product = get_object_or_404(Product, pk=product_id)

    # Get the cart from the session or create an empty cart
    cart = request.session.get('cart', {})
    
    # Update the cart with the product details
    cart[product_id] = {
        'id': product.id,
        'name': product.name,
        'price': product.price,
        # Add any other details you want in the cart
    }

    # Save the updated cart back to the session
    request.session['cart'] = cart

    # Redirect the user after adding the product to the cart
    return redirect('product_detail', product_id=product_id)


def success_view(request):
    return render(request, 'sucess.html')

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data (e.g., send email, save to database)
            # Add your logic here

            # Redirect to the 'success' URL after successful form submission
            return redirect('sucess')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    # Comment handling
    if request.method == 'POST' and 'comment_form' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.product = product
            new_comment.user = request.user
            new_comment.save()
            return redirect('product_detail', product_id=product_id)
    else:
        comment_form = CommentForm()

    # Rating handling
    if request.method == 'POST' and 'rating_form' in request.POST:
        rating_form = RatingForm(request.POST)
        if rating_form.is_valid():
            new_rating = rating_form.save(commit=False)
            new_rating.product = product
            new_rating.user = request.user
            new_rating.save()
            return redirect('product_detail', product_id=product_id)
    else:
        rating_form = RatingForm()

    # Fetch comments and ratings related to this product
    comments = Comment.objects.filter(product=product)
    ratings = Rating.objects.filter(product=product)

    context = {
        'product': product,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'comments': comments,
        'ratings': ratings,
    }
    return render(request, 'product_detail.html', context)


@login_required
def add_comment(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.product = product
            new_comment.save()
            return JsonResponse({'success': True})  # Return a success response or redirect
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form})

@login_required
def add_rating(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            new_rating = form.save(commit=False)
            new_rating.user = request.user
            new_rating.product = product
            new_rating.save()
            return JsonResponse({'success': True})  # Return a success response or redirect
    else:
        form = RatingForm()
    return render(request, 'add_rating.html', {'form': form})




