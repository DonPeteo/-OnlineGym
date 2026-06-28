from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Program,Video,PurchasedProgram, Review, Favorite
from .forms import RegisterForm, ReviewForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.models import User

def program_list(request):
    #programs = Program.objects.all()
    programs = Program.objects.all()[:3]
    total_programs = Program.objects.count()

    context = {
        'programs': programs,
        'total_programs': total_programs,
    }

    return render(request, 'core/program_list.html', context)


def program_detail(request, id):
    program = get_object_or_404(Program, id=id)

    has_purchased = False
    is_favorite = False
    user_review_exists = False

    if request.user.is_authenticated:
        has_purchased = PurchasedProgram.objects.filter(user=request.user, program=program).exists()
        is_favorite = Favorite.objects.filter(user=request.user, program=program).exists()
        user_review_exists = Review.objects.filter(user=request.user, program=program).exists()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        if not has_purchased:
            return redirect('program_detail', id=program.id)

        if user_review_exists:
            return redirect('program_detail', id=program.id)

        review_form = ReviewForm(request.POST)

        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = request.user
            review.program = program
            review.save()

            return redirect('program_detail', id=program.id)
    else:
        review_form = ReviewForm()

    context = {
        'program': program,
        'has_purchased': has_purchased,
        'is_favorite': is_favorite,
        'review_form': review_form,
        'user_review_exists': user_review_exists,
    }

    return render(request, 'core/program_detail.html', context)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('program_list')
    else:
        form = RegisterForm()

    context = {
        'form': form
    }

    return render(request, 'core/register.html', context)


@login_required
def buy_program(request, id):
    program = get_object_or_404(Program, id=id)

    PurchasedProgram.objects.get_or_create(user=request.user,program=program)

    return redirect('program_detail', id=program.id)

@login_required
def create_checkout_session(request, id):

    program = get_object_or_404(Program, id=id)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],

        line_items=[
            {
                'price_data': {
                    'currency': 'eur',
                    'product_data': {'name': program.title,},
                    'unit_amount': int(program.price_eur * 100),
                    },
                'quantity': 1,
            }],

        mode='payment',

        metadata={
            'user_id': request.user.id,
            'program_id': program.id,},

        success_url=request.build_absolute_uri(
            f'/program/{program.id}/success/'),

        cancel_url=request.build_absolute_uri(
            f'/program/{program.id}/'),
    )

    return redirect(checkout_session.url)


@login_required
def payment_success(request, id):
    program = get_object_or_404(Program, id=id)

    PurchasedProgram.objects.get_or_create(user=request.user, program=program)

    Favorite.objects.filter(user=request.user, program=program).delete()

    return redirect('program_detail', id=program.id)


@login_required
def my_programs(request):
    purchases = PurchasedProgram.objects.filter(user=request.user)

    context = {
        'purchases': purchases
    }

    return render(request, 'core/my_programs.html', context)





@login_required
def watch_video(request, id):

    video = get_object_or_404(Video, id=id)

    if video.is_preview:
        return redirect(video.video_url)

    has_purchased = PurchasedProgram.objects.filter(
        user=request.user,
        program=video.program
    ).exists()

    if not has_purchased:
        return redirect('program_detail', id=video.program.id)

    return redirect(video.video_url)


def all_programs(request):
    programs = Program.objects.all()

    context = {
        'programs': programs,
        'title': 'All Programs',
        'subtitle': 'Browse all available workout programs.',
        'show_difficulty_filter': False,
    }

    return render(request, 'core/all_programs.html', context)


def home_programs(request):
    difficulty = request.GET.get('difficulty')

    programs = Program.objects.filter(category='HOME')

    if difficulty:
        programs = programs.filter(difficulty=difficulty)

    context = {
        'programs': programs,
        'title': 'Home Workouts',
        'subtitle': 'Browse all available home workout programs.',
        'show_difficulty_filter': True,
        'current_difficulty': difficulty,
        'category_url_name': 'home_programs',
    }

    return render(request, 'core/all_programs.html', context)


def gym_programs(request):
    difficulty = request.GET.get('difficulty')

    programs = Program.objects.filter(category='GYM')

    if difficulty:
        programs = programs.filter(difficulty=difficulty)

    context = {
        'programs': programs,
        'title': 'Gym Workouts',
        'subtitle': 'Browse all available gym workout programs.',
        'show_difficulty_filter': True,
        'current_difficulty': difficulty,
        'category_url_name': 'gym_programs',
    }

    return render(request, 'core/all_programs.html', context)


@login_required
def toggle_wishlist(request, id):
    program = get_object_or_404(Program, id=id)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        program=program
    )

    if not created:
        favorite.delete()

    return redirect('program_detail', id=program.id)


@login_required
def wishlist(request):
    favorites = Favorite.objects.filter(user=request.user)

    context = {
        'favorites': favorites
    }

    return render(request, 'core/wishlist.html', context)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        user_id = session['metadata']['user_id']
        program_id = session['metadata']['program_id']

        user = User.objects.get(id=user_id)
        program = Program.objects.get(id=program_id)

        PurchasedProgram.objects.get_or_create(
            user=user,
            program=program
        )

        Favorite.objects.filter(
            user=user,
            program=program
        ).delete()

    return HttpResponse(status=200)