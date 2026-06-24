from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Program, PurchasedProgram
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe


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

    if request.user.is_authenticated:
        has_purchased = PurchasedProgram.objects.filter(user=request.user, program=program).exists()

    context = {
        'program': program,
        'has_purchased':has_purchased,
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
                    'product_data': {
                        'name': program.title,
                    },
                    'unit_amount': int(program.price_eur * 100),
                },
                'quantity': 1,
            }
        ],

        mode='payment',

        success_url=request.build_absolute_uri(
            f'/program/{program.id}/success/'
        ),

        cancel_url=request.build_absolute_uri(
            f'/program/{program.id}/'
        ),
    )

    return redirect(checkout_session.url)


@login_required
def payment_success(request, id):
    program = get_object_or_404(Program, id=id)

    PurchasedProgram.objects.get_or_create(
        user=request.user,
        program=program
    )

    return redirect('program_detail', id=program.id)


@login_required
def my_programs(request):
    purchases = PurchasedProgram.objects.filter(user=request.user)

    context = {
        'purchases': purchases
    }

    return render(request, 'core/my_programs.html', context)


def all_programs(request):
    programs = Program.objects.all()

    context = {
        'programs': programs
    }

    return render(request, 'core/all_programs.html', context)