from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from docx.enum.text import WD_UNDERLINE
from .forms import CalculationForm
from .models import Calculation
from .forms import SubscriberForm
from .forms import ContractForm
from .models import Subscriber
from decimal import ROUND_HALF_UP, Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
import os
import re
import pymorphy3
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from num2words import num2words
from django.db.models import Sum
from django.db.models import Q
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'myapp/home.html')
    
def calculation(request):
    return render(request, 'myapp/calculation.html')

def calculate_all_contracts(request):
    return render(request, 'myapp/calculate_all_contracts.html')

def calculate_single_contract(request):
    return render(request, 'myapp/calculate_single_contract.html')

def subscribers_db(request):
    return render(request, 'myapp/subscribers_db.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")  # Перенаправление на страницу статистики
        else:
            return render(request, "login.html", {"error": "Такой пользователь не зарегистрирован."})

    return render(request, "login.html")

def calculation(request):
    if request.method == 'POST':
        form = CalculationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('calculation')
    else:
        form = CalculationForm()
    calculations = Calculation.objects.all().order_by('-date_created')
    return render(request, 'myapp/calculation.html', {'form': form, 'calculations': calculations})

def subscribers_db(request):
    if request.method == 'POST':
        # Проверка, если это форма добавления нового абонента
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subscribers_db')
                
    # GET-запрос: отображение списка абонентов и формы добавления
    form = SubscriberForm()
    subscribers = Subscriber.objects.all()
    return render(request, 'myapp/subscribers_db.html', {'form': form, 'subscribers': subscribers})

def search_subscribers(request):
    query = request.GET.get('q', '')  # Получаем поисковый запрос
    results = []
    if query:
        # Ищем записи, соответствующие запросу
        results = Subscriber.objects.filter(
            name__icontains=query  # Поиск по имени
        ) | Subscriber.objects.filter(
            short_name__icontains=query  # Поиск по короткому наименованию
        ) | Subscriber.objects.filter(
            i_number__icontains=query  # Поиск по номеру договора
        ) | Subscriber.objects.filter(
            street__icontains=query  # Поиск по адресу
        )
    return render(request, 'myapp/subscribers_db.html', {'query': query, 'results': results})

def calculate_cost(subscriber, hws_node_modem_count, heating_node_modem_count, hws_node_no_modem_count,
            heating_node_no_modem_count, hws_automation_node_count, heating_automation_node_count,
            hws_node_modem_discount_count, heating_node_modem_discount_count, hws_node_no_modem_discount_count,
            heating_node_no_modem_discount_count, hws_automation_node_discount_count, heating_automation_node_discount_count,
            hws_four_year_node_count, heating_four_year_node_count, calculation):
            
            # Использование стоимости узлов из последней записи в таблице Calculation
            cost_per_hws_node_modem = calculation.service_node_modem
            cost_per_hws_node_no_modem = calculation.service_node_no_modem
            cost_per_heating_node_modem = calculation.service_node_modem
            cost_per_heating_node_no_modem = calculation.service_node_no_modem
            cost_per_automation_node = calculation.automation_node
            cost_per_four_year_node = calculation.service_four_year_node
            
            # Стоимость узлов со скидкой
            cost_per_hws_node_modem_discount = cost_per_hws_node_modem * Decimal(0.5)
            cost_per_hws_node_no_modem_discount = cost_per_hws_node_no_modem * Decimal(0.5)
            cost_per_heating_node_modem_discount = cost_per_heating_node_modem * Decimal(0.5)
            cost_per_heating_node_no_modem_discount = cost_per_heating_node_no_modem * Decimal(0.5)
            cost_per_automation_node_discount = calculation.automation_node * Decimal(0.5)
            
            # Расчет НДС
            nds_node_modem = cost_per_hws_node_modem * Decimal(0.2) # НДС учет с модемом
            nds_node_modem_discount = cost_per_hws_node_modem_discount * Decimal(0.2) # НДС учет с модемом со скидкой
            nds_node_no_modem = cost_per_hws_node_no_modem * Decimal(0.2) # НДС учет без модема
            nds_node_no_modem_discount = cost_per_hws_node_no_modem_discount * Decimal(0.2) # НДС учет без модема сщ скидкой
            nds_automation_node = cost_per_automation_node * Decimal(0.2) # НДС автоматика
            nds_automation_node_discount = cost_per_automation_node_discount * Decimal(0.2) # НДС автоматика со скидкой
            nds_four_year_node = cost_per_four_year_node * Decimal(0.2) # НДС узлов до 4-х лет
            
            # Расчет стоимости
            hws_node_modem_month = cost_per_hws_node_modem * hws_node_modem_count # Сумма узлов ГВС за месяц без НДС
            hws_node_modem_discount_month = cost_per_hws_node_modem_discount * hws_node_modem_discount_count # Сумма узлов ГВС за месяц без НДС со скидкой
            hws_node_no_modem_month = cost_per_hws_node_no_modem * hws_node_no_modem_count # Сумма узлов ГВС без модема за месяц без НДС
            hws_node_no_modem_discount_month = cost_per_hws_node_no_modem_discount * hws_node_no_modem_discount_count # Сумма узлов ГВС без модема за месяц без НДС со скидкой
            heating_node_modem_month = cost_per_heating_node_modem * heating_node_modem_count # Сумма узлов отопления за месяц без НДС
            heating_node_modem_discount_month = cost_per_heating_node_modem_discount * heating_node_modem_discount_count # Сумма узлов отопления за месяц без НДС со скидкой
            heating_node_no_modem_month = cost_per_heating_node_no_modem * heating_node_no_modem_count # Сумма узлов отопления без модема за месяц без НДС
            heating_node_no_modem_discount_month = cost_per_heating_node_no_modem_discount * heating_node_no_modem_discount_count # Сумма узлов отопления без модема за месяц без НДС со скидкой
            hws_automation_node_month = cost_per_automation_node * hws_automation_node_count # Сумма узлов автоматики ГВС за месяц без НДС
            hws_automation_node_discount_month = cost_per_automation_node_discount * hws_automation_node_discount_count # Сумма узлов автоматики ГВС за месяц без НДС со скидкой
            heating_automation_node_month = cost_per_automation_node * heating_automation_node_count # Сумма узлов автоматики отопления за месяц без НДС
            heating_automation_node_discount_month = cost_per_automation_node_discount * heating_automation_node_discount_count # Сумма узлов автоматики отопления за месяц без НДС со скидкой
            hws_four_year_node_month = cost_per_four_year_node * hws_four_year_node_count # Сумма узлов ГВС до 4=х лет за месяц без НДС
            heating_four_year_node_month = cost_per_four_year_node * heating_four_year_node_count # Сумма узлов отопления до 4=х лет за месяц без НДС

            hws_modem_cost = ((cost_per_hws_node_modem + nds_node_modem) * hws_node_modem_count) * Decimal(12) # Сумма узлов ГВС с модемом в год с НДС
            hws_modem_discount_cost = ((cost_per_hws_node_modem_discount + nds_node_modem_discount) * hws_node_modem_discount_count) * Decimal(12) # Сумма узлов ГВС с модемом со скидкой в год с НДС
            hws_no_modem_cost = ((cost_per_hws_node_no_modem + nds_node_no_modem) * hws_node_no_modem_count) * Decimal(12) # Сумма узлов ГВС без модема в год с НДС
            hws_no_modem_discount_cost = ((cost_per_hws_node_no_modem_discount + nds_node_no_modem_discount) * hws_node_no_modem_discount_count) * Decimal(12) # Сумма узлов ГВС без модема со скидкой в год с НДС
            heating_modem_cost = ((cost_per_heating_node_modem + nds_node_modem) * heating_node_modem_count) * Decimal(8) # Сумма узлов отопления в год с НДС
            heating_modem_discount_cost = ((cost_per_heating_node_modem_discount + nds_node_modem_discount) * heating_node_modem_discount_count) * Decimal(8) # Сумма узлов отопления с модемом со скидкой в год с НДС
            heating_no_modem_cost = ((cost_per_heating_node_no_modem + nds_node_no_modem) * heating_node_no_modem_count) * Decimal(8) # Сумма узлов отопления без модема в год с НДС
            heating_no_modem_discount_cost = ((cost_per_heating_node_no_modem_discount + nds_node_no_modem_discount) * heating_node_no_modem_discount_count) * Decimal(8) # Сумма узлов отопления без модема  со скидкой в год с НДС
            hws_automation_cost = ((cost_per_automation_node + nds_automation_node) * hws_automation_node_count) * Decimal(12) # Сумма узлов автоматики ГВС в год с НДС
            hws_automation_discount_cost = ((cost_per_automation_node_discount + nds_automation_node_discount) * hws_automation_node_discount_count) * Decimal(12) # Сумма узлов автоматики ГВС со скидкой в год с НДС
            heating_automation_cost = ((cost_per_automation_node + nds_automation_node) * heating_automation_node_count) * Decimal(8) # Сумма узлов автоматики отопления в год с НДС
            heating_automation_discount_cost = ((cost_per_automation_node_discount + nds_automation_node_discount) * heating_automation_node_discount_count) * Decimal(8) # Сумма узлов автоматики отопления со скидкой в год с НДС
            hws_four_year_cost = ((cost_per_four_year_node + nds_four_year_node) * hws_four_year_node_count) * Decimal(12) # Сумма узлов ГВС до 4-х лет в год
            heating_four_year_cost = ((cost_per_four_year_node + nds_four_year_node) * heating_four_year_node_count) * Decimal(8) # Сумма узлов отопления до 4-х лет в год

            total_nds_month = (nds_node_modem * hws_node_modem_count) + (nds_node_modem * heating_node_modem_count) + (nds_node_no_modem * hws_node_no_modem_count) + (nds_node_no_modem * heating_node_no_modem_count) + (nds_automation_node * hws_automation_node_count) + (nds_automation_node * heating_automation_node_count) + (nds_four_year_node * hws_four_year_node_count) + (nds_four_year_node * heating_four_year_node_count) + (nds_node_modem_discount * hws_node_modem_discount_count) + (nds_node_modem_discount * heating_node_modem_discount_count) + (nds_node_no_modem_discount * hws_node_no_modem_discount_count) + (nds_node_no_modem_discount * heating_node_no_modem_discount_count) + (nds_automation_node_discount * hws_automation_node_discount_count) + (nds_automation_node_discount * heating_automation_node_discount_count)# Сумма НДС в месяц
            total_cost_month = hws_node_modem_month + heating_node_modem_month + hws_node_no_modem_month + heating_node_no_modem_month + hws_automation_node_month + heating_automation_node_month + hws_four_year_node_month + heating_four_year_node_month + hws_node_modem_discount_month + heating_node_modem_discount_month + hws_node_no_modem_discount_month + heating_node_no_modem_discount_month + hws_automation_node_discount_month + heating_automation_node_discount_month # Итого в месяц без НДС
            total_cost = hws_modem_cost + hws_no_modem_cost + heating_modem_cost + heating_no_modem_cost + hws_automation_cost + heating_automation_cost + hws_four_year_cost + heating_four_year_cost + hws_modem_discount_cost + hws_no_modem_discount_cost + heating_modem_discount_cost + heating_no_modem_discount_cost + hws_automation_discount_cost + heating_automation_discount_cost
            total_nds_month = total_nds_month.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_cost_month_nds = total_cost_month + total_nds_month # Сумма в месяц с НДС
            total_nds_year = (nds_node_modem * hws_node_modem_count * Decimal(12)) + (nds_node_modem * heating_node_modem_count * Decimal(8)) + (nds_node_no_modem * hws_node_no_modem_count * Decimal(12)) + (nds_node_no_modem * heating_node_no_modem_count * Decimal(8)) + (nds_automation_node * hws_automation_node_count * Decimal(12)) + (nds_automation_node * heating_automation_node_count * Decimal(8)) + (nds_four_year_node * hws_four_year_node_count * Decimal(12)) + (nds_four_year_node * heating_four_year_node_count * Decimal(8)) # Сумма НДС в год
            total_nds_year = total_nds_year.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_cost = total_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) 
            
            subscriber.total_cost = total_cost
            subscriber.save()
            
            return hws_automation_node_month, heating_automation_node_month, heating_automation_node_discount_month, hws_node_modem_month, hws_node_no_modem_month, hws_node_modem_discount_month, heating_node_modem_month, heating_node_no_modem_month, heating_node_modem_discount_month, hws_four_year_node_month, heating_four_year_node_month, total_cost, total_nds_year, total_cost_month_nds, total_cost_month, total_nds_month

def calculate_single_contract(request):
    calculation = Calculation.objects.latest('date_created')  # Получение последней записи в таблице Calculation
    if request.method == 'POST':
        form = ContractForm(request.POST)
        if form.is_valid():
            # Количество узлов
            hws_node_modem_count = form.cleaned_data['hws_node_modem']
            hws_node_modem_discount_count = form.cleaned_data['hws_node_modem_discount']
            heating_node_modem_count = form.cleaned_data['heating_node_modem']
            heating_node_modem_discount_count = form.cleaned_data['heating_node_modem_discount']
            hws_node_no_modem_count = form.cleaned_data['hws_node_no_modem']
            hws_node_no_modem_discount_count = form.cleaned_data['hws_node_no_modem_discount']
            heating_node_no_modem_count = form.cleaned_data['heating_node_no_modem']
            heating_node_no_modem_discount_count = form.cleaned_data['heating_node_no_modem_discount']
            hws_automation_node_count = form.cleaned_data['hws_automation_node']
            hws_automation_node_discount_count = form.cleaned_data['hws_automation_node_discount']
            heating_automation_node_count = form.cleaned_data['heating_automation_node']
            heating_automation_node_discount_count = form.cleaned_data['heating_automation_node_discount']
            hws_four_year_node_count = form.cleaned_data['hws_four_year_node']
            heating_four_year_node_count = form.cleaned_data['heating_four_year_node']
                        
            # Использование стоимости узлов из последней записи в таблице Calculation
            cost_per_hws_node_modem = calculation.service_node_modem
            cost_per_hws_node_no_modem = calculation.service_node_no_modem
            cost_per_heating_node_modem = calculation.service_node_modem
            cost_per_heating_node_no_modem = calculation.service_node_no_modem
            cost_per_automation_node = calculation.automation_node
            cost_per_four_year_node = calculation.service_four_year_node
            
            # Стоимость узлов со скидкой
            cost_per_hws_node_modem_discount = cost_per_hws_node_modem * Decimal(0.5)
            cost_per_hws_node_no_modem_discount = cost_per_hws_node_no_modem * Decimal(0.5)
            cost_per_heating_node_modem_discount = cost_per_heating_node_modem * Decimal(0.5)
            cost_per_heating_node_no_modem_discount = cost_per_heating_node_no_modem * Decimal(0.5)
            cost_per_automation_node_discount = calculation.automation_node * Decimal(0.5)
            
            # Расчет НДС
            nds_node_modem = cost_per_hws_node_modem * Decimal(0.2) # НДС учет с модемом
            nds_node_modem_discount = cost_per_hws_node_modem_discount * Decimal(0.2) # НДС учет с модемом со скидкой
            nds_node_no_modem = cost_per_hws_node_no_modem * Decimal(0.2) # НДС учет без модема
            nds_node_no_modem_discount = cost_per_hws_node_no_modem_discount * Decimal(0.2) # НДС учет без модема сщ скидкой
            nds_automation_node = cost_per_automation_node * Decimal(0.2) # НДС автоматика
            nds_automation_node_discount = cost_per_automation_node_discount * Decimal(0.2) # НДС автоматика со скидкой
            nds_four_year_node = cost_per_four_year_node * Decimal(0.2) # НДС узлов до 4-х лет
            
            # Расчет стоимости
            hws_node_modem_month = cost_per_hws_node_modem * hws_node_modem_count # Сумма узлов ГВС за месяц без НДС
            hws_node_modem_discount_month = cost_per_hws_node_modem_discount * hws_node_modem_discount_count # Сумма узлов ГВС за месяц без НДС со скидкой
            hws_node_no_modem_month = cost_per_hws_node_no_modem * hws_node_no_modem_count # Сумма узлов ГВС без модема за месяц без НДС
            hws_node_no_modem_discount_month = cost_per_hws_node_no_modem_discount * hws_node_no_modem_discount_count # Сумма узлов ГВС без модема за месяц без НДС со скидкой
            heating_node_modem_month = cost_per_heating_node_modem * heating_node_modem_count # Сумма узлов отопления за месяц без НДС
            heating_node_modem_discount_month = cost_per_heating_node_modem_discount * heating_node_modem_discount_count # Сумма узлов отопления за месяц без НДС со скидкой
            heating_node_no_modem_month = cost_per_heating_node_no_modem * heating_node_no_modem_count # Сумма узлов отопления без модема за месяц без НДС
            heating_node_no_modem_discount_month = cost_per_heating_node_no_modem_discount * heating_node_no_modem_discount_count # Сумма узлов отопления без модема за месяц без НДС со скидкой
            hws_automation_node_month = cost_per_automation_node * hws_automation_node_count # Сумма узлов автоматики ГВС за месяц без НДС
            hws_automation_node_discount_month = cost_per_automation_node_discount * hws_automation_node_discount_count # Сумма узлов автоматики ГВС за месяц без НДС со скидкой
            heating_automation_node_month = cost_per_automation_node * heating_automation_node_count # Сумма узлов автоматики отопления за месяц без НДС
            heating_automation_node_discount_month = cost_per_automation_node_discount * heating_automation_node_discount_count # Сумма узлов автоматики отопления за месяц без НДС со скидкой
            hws_four_year_node_month = cost_per_four_year_node * hws_four_year_node_count # Сумма узлов ГВС до 4=х лет за месяц без НДС
            heating_four_year_node_month = cost_per_four_year_node * heating_four_year_node_count # Сумма узлов отопления до 4=х лет за месяц без НДС

            hws_modem_cost = ((cost_per_hws_node_modem + nds_node_modem) * hws_node_modem_count) * Decimal(12) # Сумма узлов ГВС с модемом в год с НДС
            hws_modem_discount_cost = ((cost_per_hws_node_modem_discount + nds_node_modem_discount) * hws_node_modem_discount_count) * Decimal(12) # Сумма узлов ГВС с модемом со скидкой в год с НДС
            hws_no_modem_cost = ((cost_per_hws_node_no_modem + nds_node_no_modem) * hws_node_no_modem_count) * Decimal(12) # Сумма узлов ГВС без модема в год с НДС
            hws_no_modem_discount_cost = ((cost_per_hws_node_no_modem_discount + nds_node_no_modem_discount) * hws_node_no_modem_discount_count) * Decimal(12) # Сумма узлов ГВС без модема со скидкой в год с НДС
            heating_modem_cost = ((cost_per_heating_node_modem + nds_node_modem) * heating_node_modem_count) * Decimal(8) # Сумма узлов отопления в год с НДС
            heating_modem_discount_cost = ((cost_per_heating_node_modem_discount + nds_node_modem_discount) * heating_node_modem_discount_count) * Decimal(8) # Сумма узлов отопления с модемом со скидкой в год с НДС
            heating_no_modem_cost = ((cost_per_heating_node_no_modem + nds_node_no_modem) * heating_node_no_modem_count) * Decimal(8) # Сумма узлов отопления без модема в год с НДС
            heating_no_modem_discount_cost = ((cost_per_heating_node_no_modem_discount + nds_node_no_modem_discount) * heating_node_no_modem_discount_count) * Decimal(8) # Сумма узлов отопления без модема  со скидкой в год с НДС
            hws_automation_cost = ((cost_per_automation_node + nds_automation_node) * hws_automation_node_count) * Decimal(12) # Сумма узлов автоматики ГВС в год с НДС
            hws_automation_discount_cost = ((cost_per_automation_node_discount + nds_automation_node_discount) * hws_automation_node_discount_count) * Decimal(12) # Сумма узлов автоматики ГВС со скидкой в год с НДС
            heating_automation_cost = ((cost_per_automation_node + nds_automation_node) * heating_automation_node_count) * Decimal(8) # Сумма узлов автоматики отопления в год с НДС
            heating_automation_discount_cost = ((cost_per_automation_node_discount + nds_automation_node_discount) * heating_automation_node_discount_count) * Decimal(8) # Сумма узлов автоматики отопления со скидкой в год с НДС
            hws_four_year_cost = ((cost_per_four_year_node + nds_four_year_node) * hws_four_year_node_count) * Decimal(12) # Сумма узлов ГВС до 4-х лет в год
            heating_four_year_cost = ((cost_per_four_year_node + nds_four_year_node) * heating_four_year_node_count) * Decimal(8) # Сумма узлов отопления до 4-х лет в год

            total_nds_month = (nds_node_modem * hws_node_modem_count) + (nds_node_modem * heating_node_modem_count) + (nds_node_no_modem * hws_node_no_modem_count) + (nds_node_no_modem * heating_node_no_modem_count) + (nds_automation_node * hws_automation_node_count) + (nds_automation_node * heating_automation_node_count) + (nds_four_year_node * hws_four_year_node_count) + (nds_four_year_node * heating_four_year_node_count) + (nds_node_modem_discount * hws_node_modem_discount_count) + (nds_node_modem_discount * heating_node_modem_discount_count) + (nds_node_no_modem_discount * hws_node_no_modem_discount_count) + (nds_node_no_modem_discount * heating_node_no_modem_discount_count) + (nds_automation_node_discount * hws_automation_node_discount_count) + (nds_automation_node_discount * heating_automation_node_discount_count)# Сумма НДС в месяц
            total_cost_month = hws_node_modem_month + heating_node_modem_month + hws_node_no_modem_month + heating_node_no_modem_month + hws_automation_node_month + heating_automation_node_month + hws_four_year_node_month + heating_four_year_node_month + hws_node_modem_discount_month + heating_node_modem_discount_month + hws_node_no_modem_discount_month + heating_node_no_modem_discount_month + hws_automation_node_discount_month + heating_automation_node_discount_month # Итого в месяц без НДС
            total_cost = hws_modem_cost + hws_no_modem_cost + heating_modem_cost + heating_no_modem_cost + hws_automation_cost + heating_automation_cost + hws_four_year_cost + heating_four_year_cost + hws_modem_discount_cost + hws_no_modem_discount_cost + heating_modem_discount_cost + heating_no_modem_discount_cost + hws_automation_discount_cost + heating_automation_discount_cost
            total_nds_month = total_nds_month.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_cost_month_nds = total_cost_month + total_nds_month # Сумма в месяц с НДС
            total_nds_year = (nds_node_modem * hws_node_modem_count * Decimal(12)) + (nds_node_modem * heating_node_modem_count * Decimal(8)) + (nds_node_no_modem * hws_node_no_modem_count * Decimal(12)) + (nds_node_no_modem * heating_node_no_modem_count * Decimal(8)) + (nds_automation_node * hws_automation_node_count * Decimal(12)) + (nds_automation_node * heating_automation_node_count * Decimal(8)) + (nds_four_year_node * hws_four_year_node_count * Decimal(12)) + (nds_four_year_node * heating_four_year_node_count * Decimal(8)) # Сумма НДС в год
            total_nds_year = total_nds_year.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total_cost = total_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) 
            
            calculation = Calculation.objects.last()
            
            #if 'calculate' in request.POST:
            calculated_data = {
                    """'i_number': form.cleaned_data['i_number'],
                    'name': form.cleaned_data['name'],
                    'short_name': form.cleaned_data['short_name'],
                    'fio': form.cleaned_data['fio'],                    
                    'post_index': form.cleaned_data['post_index'],
                    'street': form.cleaned_data['street'],
                    'house': form.cleaned_data['house'],
                    'inn': form.cleaned_data['inn'],
                    'account_number': form.cleaned_data['account_number'],
                    'corr_account': form.cleaned_data['corr_account'],
                    'bik': form.cleaned_data['bik'],
                    'kpp': form.cleaned_data['kpp'],
                    'ogrn': form.cleaned_data['ogrn'],
                    'l_number': form.cleaned_data['l_number'],
                    'bank_name': form.cleaned_data['bank_name'],
                    'post': form.cleaned_data['post'],"""
                    'hws_node_modem_count': hws_node_modem_count,
                    'hws_node_modem_discount_count': hws_node_modem_discount_count,
                    'hws_node_no_modem_count': hws_node_no_modem_count,
                    'hws_node_no_modem_discount_count': hws_node_no_modem_discount_count,
                    'heating_node_modem_count': heating_node_modem_count,
                    'heating_node_modem_discount_count': heating_node_modem_discount_count,
                    'heating_node_no_modem_count': heating_node_no_modem_count,
                    'heating_node_no_modem_discount_count': heating_node_no_modem_discount_count,
                    'hws_four_year_node_count': hws_four_year_node_count,
                    'heating_four_year_node_count': heating_four_year_node_count,
                    'hws_automation_node_count': hws_automation_node_count,
                    'hws_automation_node_discount_count': hws_automation_node_discount_count,
                    'heating_automation_node_count': heating_automation_node_count,
                    'heating_automation_node_discount_count': heating_automation_node_discount_count,
                    'cost_per_hws_node_modem': cost_per_hws_node_modem,
                    'cost_per_hws_node_modem_discount': cost_per_hws_node_modem_discount,
                    'cost_per_hws_node_no_modem': cost_per_hws_node_no_modem,
                    'cost_per_hws_node_no_modem_discount': cost_per_hws_node_no_modem_discount,
                    'cost_per_heating_node_modem': cost_per_heating_node_modem,
                    'cost_per_heating_node_modem_discount': cost_per_heating_node_modem_discount,
                    'cost_per_heating_node_no_modem': cost_per_heating_node_no_modem,
                    'cost_per_heating_node_no_modem_discount': cost_per_heating_node_no_modem_discount,
                    'cost_per_four_year_node': cost_per_four_year_node,
                    'hws_node_modem_month': hws_node_modem_month,
                    'hws_node_modem_discount_month': hws_node_modem_discount_month,
                    'heating_node_modem_month': heating_node_modem_month,
                    'heating_node_modem_discount_month': heating_node_modem_discount_month,
                    'hws_node_no_modem_month': hws_node_no_modem_month,
                    'hws_node_no_modem_discount_month': hws_node_no_modem_discount_month,
                    'heating_node_no_modem_month': heating_node_no_modem_month,
                    'heating_node_no_modem_discount_month': heating_node_no_modem_discount_month,
                    'cost_per_automation_node': cost_per_automation_node,
                    'cost_per_automation_node_discount': cost_per_automation_node_discount,
                    'hws_automation_node_month': hws_automation_node_month,
                    'hws_automation_node_discount_month': hws_automation_node_discount_month,
                    'heating_automation_node_month': heating_automation_node_month,
                    'heating_automation_node_discount_month': heating_automation_node_discount_month,
                    'hws_four_year_node_month': hws_four_year_node_month,
                    'heating_four_year_node_month': heating_four_year_node_month,
                    'total_cost_month': total_cost_month,
                    'total_nds_month': total_nds_month,
                    'total_cost_month_nds': total_cost_month_nds,
                    'total_nds_year': total_nds_year,
                    'total_cost': total_cost,
                    }
                
            return render(request, 'myapp/calculate_single_contract.html', {'form': form, 'calculated_data': calculated_data})
            #elif 'save' in request.POST:
            form.save()
            return redirect('calculate_single_contract')
    else:
        form = ContractForm()
    return render(request, 'myapp/calculate_single_contract.html', {
        'form': form, 
        'cost_per_hws_node_modem': calculation.service_node_modem, 
        'cost_per_hws_node_no_modem': calculation.service_node_no_modem, 
        'cost_per_heating_node_modem': calculation.service_node_modem, 
        'cost_per_heating_node_no_modem': calculation.service_node_no_modem,
        'cost_per_automation_node': calculation.automation_node,
    })
        
def edit_subscriber(request, id):
    subscriber = get_object_or_404(Subscriber, id=id)
    if request.method == 'POST':
        form = SubscriberForm(request.POST, instance=subscriber)
        if form.is_valid():
            form.save()
            return redirect('subscribers_db')
    else:
            form = SubscriberForm(instance=subscriber)
    return render(request, 'myapp/edit_subscriber.html', {'form': form, 'subscriber': subscriber})
    
def delete_subscriber(request, id):
    subscriber = get_object_or_404(Subscriber, id=id)
    subscriber.delete()
    return redirect('subscribers_db')

def calculate_all_contracts(request):
    # Попытка получить последнюю запись из модели Calculation
    try:
        calculation = Calculation.objects.latest('id')
    except Calculation.DoesNotExist:
        return render(request, 'myapp/calculate_all_contracts.html', {
            'message': 'Нет доступных данных для расчёта.'
        })

    search_query = request.GET.get('search', '').strip()  # Получаем поисковый запрос
    subscribers = Subscriber.objects.all()

    # Если введен запрос, фильтруем список абонентов
    if search_query:
        subscribers = subscribers.filter(
            Q(name__icontains=search_query) |
            Q(short_name__icontains=search_query) |
            Q(inn__icontains=search_query) |
            Q(street__icontains=search_query)
        )

    results = []
    for subscriber in subscribers:
        # Вызов функции расчёта
        hws_automation_node_month, heating_automation_node_month, heating_automation_node_discount_month, hws_node_modem_month, hws_node_no_modem_month, hws_node_modem_discount_month, heating_node_modem_month, heating_node_no_modem_month, heating_node_modem_discount_month, hws_four_year_node_month, heating_four_year_node_month, total_cost, total_nds_year, total_cost_month_nds, total_cost_month, total_nds_month = calculate_cost(
            subscriber=subscriber,
            hws_node_modem_count=subscriber.hws_node_modem,
            hws_node_modem_discount_count=subscriber.hws_node_modem_discount,
            heating_node_modem_count=subscriber.heating_node_modem,
            heating_node_modem_discount_count=subscriber.heating_node_modem_discount,
            hws_node_no_modem_count=subscriber.hws_node_no_modem,
            hws_node_no_modem_discount_count=subscriber.hws_node_no_modem_discount,
            heating_node_no_modem_count=subscriber.heating_node_no_modem,
            heating_node_no_modem_discount_count=subscriber.heating_node_no_modem_discount,
            hws_automation_node_count=subscriber.hws_automation_node,
            hws_automation_node_discount_count=subscriber.hws_automation_node_discount,
            heating_automation_node_count=subscriber.heating_automation_node,
            heating_automation_node_discount_count=subscriber.heating_automation_node_discount,
            hws_four_year_node_count=subscriber.hws_four_year_node,
            heating_four_year_node_count=subscriber.heating_four_year_node,
            calculation=calculation
        )

        results.append({
            'name': subscriber.name,
            'short_name': subscriber.short_name,
            'street': subscriber.street,
            'house': subscriber.house,
            'inn': subscriber.inn,
            'i_number': subscriber.i_number,
            'account_number': subscriber.account_number,
            'corr_account': subscriber.corr_account,
            'bik': subscriber.bik,
            'kpp': subscriber.kpp,
            'ogrn': subscriber.ogrn,
            'l_number': subscriber.l_number,
            'bank_name': subscriber.bank_name,
            'hws_node_modem_count': subscriber.hws_node_modem,
            'hws_node_modem_discount_count': subscriber.hws_node_modem_discount,
            'heating_node_modem_count': subscriber.heating_node_modem,
            'heating_node_modem_discount_count': subscriber.heating_node_modem_discount,
            'hws_node_no_modem_count': subscriber.hws_node_no_modem,
            'hws_node_no_modem_discount_count': subscriber.hws_node_no_modem_discount,
            'heating_node_no_modem_count': subscriber.heating_node_no_modem,
            'heating_node_no_modem_discount_count': subscriber.heating_node_no_modem_discount,
            'hws_automation_node_count': subscriber.hws_automation_node,
            'hws_automation_node_discount_count': subscriber.hws_automation_node_discount,
            'heating_automation_node_count': subscriber.heating_automation_node,
            'heating_automation_node_discount_count': subscriber.heating_automation_node_discount,
            'hws_four_year_node_count': subscriber.hws_four_year_node,
            'heating_four_year_node_count': subscriber.heating_four_year_node,
            'hws_node_modem_month': hws_node_modem_month,
            'hws_node_no_modem_month': hws_node_no_modem_month,
            'hws_node_modem_discount_month': hws_node_modem_discount_month,
            'hws_automation_node_month': hws_automation_node_month,
            'heating_node_modem_month': heating_node_modem_month,
            'heating_node_no_modem_month': heating_node_no_modem_month,
            'heating_node_modem_discount_month': heating_node_modem_discount_month,
            'heating_automation_node_month': heating_automation_node_month,
            'heating_automation_node_discount_month': heating_automation_node_discount_month,
            'hws_four_year_node_month': hws_four_year_node_month,
            'heating_four_year_node_month': heating_four_year_node_month,
            'cost_per_hws_node_modem': calculation.service_node_modem,
            'cost_per_hws_node_modem_discount': calculation.service_node_modem * Decimal(0.5),
            'cost_per_heating_node_modem': calculation.service_node_modem,
            'cost_per_heating_node_modem_discount': calculation.service_node_modem * Decimal(0.5),
            'cost_per_hws_node_no_modem': calculation.service_node_no_modem,
            'cost_per_hws_node_no_modem_discount': calculation.service_node_no_modem * Decimal(0.5),
            'cost_per_heating_node_no_modem': calculation.service_node_no_modem,
            'cost_per_heating_node_no_modem_discount': calculation.service_node_no_modem * Decimal(0.5),
            'cost_per_automation_node': calculation.automation_node,
            'cost_per_automation_node_discount': calculation.automation_node * Decimal(0.5),
            'cost_per_four_year_node': calculation.service_four_year_node,
            'total_cost': total_cost,
            'total_nds_year': total_nds_year,
            'total_cost_month': total_cost_month,
            'total_nds_month': total_nds_month,
            'total_cost_month_nds': total_cost_month_nds,
        })

    return render(request, 'myapp/calculate_all_contracts.html', {
        'results': results,
        'search_query': search_query  # Передаем текущий запрос в шаблон
    })

def home(request):
    # Рассчитываем общую сумму всех договоров
    total_contract_sum = Subscriber.objects.aggregate(Sum('total_cost'))['total_cost__sum'] or 0

    # Преобразуем в Decimal и округляем до двух знаков после запятой
    total_contract_sum = Decimal(total_contract_sum).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

    # Общее количество абонентов
    subscriber_count = Subscriber.objects.count()

    # Количество всех узлов учета
    total_nodes = (
        Subscriber.objects.aggregate(
            total_hws=Sum('hws_node_modem') + Sum('hws_node_no_modem') + Sum('hws_node_modem_discount') + Sum('hws_node_no_modem_discount'),
            total_heating=Sum('heating_node_modem') + Sum('heating_node_no_modem') + Sum('heating_node_modem_discount') + Sum('heating_node_no_modem_discount'),
            total_automation=Sum('hws_automation_node') + Sum('hws_automation_node_discount') + Sum('heating_automation_node') + Sum('heating_automation_node_discount'),
            total_automation_hws=Sum('hws_automation_node') + Sum('hws_automation_node_discount'),
            total_automation_heating=Sum('heating_automation_node') + Sum('heating_automation_node_discount'),
            total_four_year=Sum('hws_four_year_node') + Sum('heating_four_year_node'),
            total_hws_discount=Sum('hws_node_modem_discount') + Sum('hws_node_no_modem_discount'),
            total_heating_discount=Sum('heating_node_modem_discount') + Sum('heating_node_no_modem_discount'),
            total_automation_hws_discount=Sum('hws_automation_node_discount'),
            total_automation_heating_discount=Sum('heating_automation_node_discount')
        )
    )

    # Рассчитываем изменения стоимости услуг
    calculations = Calculation.objects.order_by('-date_created')  # Сортируем по убыванию даты
    statistics = []
    for i in range(1, len(calculations)):
        previous = calculations[i]
        current = calculations[i - 1]

        def calculate_change(current_value, previous_value):
            if previous_value == 0:
                return None  # Если предыдущая стоимость равна нулю, изменения не рассчитываются
            change = ((current_value - previous_value) / previous_value) * 100
            return Decimal(change).quantize(Decimal('0.01'))  # Округление до двух знаков

        stats = {
            'date': current.date_created,
            'service_node_modem_change': calculate_change(current.service_node_modem, previous.service_node_modem),
            'service_node_no_modem_change': calculate_change(current.service_node_no_modem, previous.service_node_no_modem),
            'automation_node_change': calculate_change(current.automation_node, previous.automation_node),
            'service_four_year_node_change': calculate_change(current.service_four_year_node, previous.service_four_year_node),
        }
        statistics.append(stats)

    # Наиболее прибыльные абоненты (топ-3)
    top_subscribers_up = Subscriber.objects.order_by('-total_cost')[:3]
    top_subscribers_down = Subscriber.objects.order_by('total_cost')[:3]

    # Подготовка данных для шаблона
    context = {
        'subscriber_count': subscriber_count,
        'total_contract_sum': total_contract_sum,
        'total_hws_nodes': total_nodes['total_hws'] or 0,
        'total_hws_discount': total_nodes['total_hws_discount'] or 0,
        'total_heating_nodes': total_nodes['total_heating'] or 0,
        'total_heating_discount': total_nodes['total_heating_discount'] or 0,
        'total_automation_hws': total_nodes['total_automation_hws'] or 0,
        'total_automation_hws_discount': total_nodes['total_automation_hws_discount'] or 0,
        'total_automation_heating': total_nodes['total_automation_heating'] or 0,
        'total_automation_heating_discount': total_nodes['total_automation_heating_discount'] or 0,
        'total_four_year_nodes': total_nodes['total_four_year'] or 0,
        'total_nodes': (
            (total_nodes['total_hws'] or 0) +
            (total_nodes['total_heating'] or 0) +
            (total_nodes['total_automation_hws'] or 0) +
            (total_nodes['total_automation_heating'] or 0) +
            (total_nodes['total_four_year'] or 0) + 
            (total_nodes['total_hws_discount'] or 0) + 
            (total_nodes['total_heating_discount'] or 0) + 
            (total_nodes['total_automation_hws_discount'] or 0) + 
            (total_nodes['total_automation_heating_discount'] or 0)
        ),
        'statistics': statistics,
        'top_subscribers_up': top_subscribers_up,  # Передаём топ-3 абонентов
        'top_subscribers_down': top_subscribers_down,
    }

    return render(request, 'myapp/home.html', context)

def add_subscriber(request):
    if request.method == "POST":
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subscribers_db')  # Перенаправление на список абонентов
    else:
        form = SubscriberForm()
    
    return render(request, 'myapp/add_subscriber.html', {'form': form})
