from django.shortcuts import render,redirect
from .models import Need,Kind
from .forms import AddNeedForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.paginator import Paginator
from django.contrib.auth import login
from appuser.models import AppUser
from django.template.defaultfilters import slugify

# Create your views here.

def get_month_name(needs):
    months = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
    for need in needs:
        need.month_name = months[need.created.month-1]

def detail_view(request,year,month,day,slug):
    try:
        need = Need.objects.get(created__year=year,created__month=month,created__day=day,slug=slug)
        if need.needy == request.user or need.donor == request.user or need.status == 'publish':
            return render(request,'need/detail.html',{'need':need})        
        return render(request,'need/detail.html',{'need':None})
    except ObjectDoesNotExist:
        return render(request,'need/detail.html',{'need':None})

def list_view(request):
    needs = list(Need.publish.all())
    get_month_name(needs)
    paginator = Paginator(needs,25)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    kinds = list(Kind.objects.all())


    current = page.number
    total = paginator.num_pages
    start = max(current - 3, 1)
    end = min(current + 3, total) + 1
    page_range = range(start, end)


    return render(request,'need/list.html',{'needs':page,'page_range':page_range,'page_obj':page,'kinds':kinds,'len':len(needs)})

def kind_view(request,slug):
    kind = Kind.objects.get(slug=slug)
    needs = Need.publish.filter(kind=kind)
    get_month_name(needs)
    paginator = Paginator(needs,25)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    kinds = list(Kind.objects.all())


    current = page.number
    total = paginator.num_pages
    start = max(current - 3, 1)
    end = min(current + 3, total) + 1
    page_range = range(start, end)


    return render(request,'need/list.html',{'needs':page,'page_range':page_range,'page_obj':page,'kinds':kinds,'len':len(needs)})

def create_username(firstname):
    username = slugify(firstname)
    counter = 0
    while User.objects.filter(username = username+str(counter)).exists():
        counter +=1
    return username+str(counter)


def add_control(tel):
    if AppUser.objects.filter(tel=tel).exists():
        raise ValidationError('Telefon numarası zaten kayıtlı. Lütfen giriş yapınız.')

def add_view(request):
    if request.method == "POST":
        form = AddNeedForm(request.POST,user = request.user if request.user.is_authenticated else None)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        name = request.POST.get('name')
        kind = request.POST.get('kind')
        kind = Kind.objects.get(id=kind)
        if request.user.is_authenticated:
            needy = User.objects.get(username = request.user.username)
            need = Need(latitude=latitude,longitude=longitude,name=name,kind=kind,needy=needy)
            need.save()
        else:
            tel = request.POST.get('tel')
            try:
                add_control(tel=tel)
                user = User(username=create_username(firstname=first_name),password=tel,first_name=first_name,last_name=last_name)
                user.save()
                AppUser.objects.create(tel=tel,user=user)
                login(request=request,user=user)
                need = Need(latitude=latitude,longitude=longitude,name=name,kind=kind,needy=user)
                need.save()
            except ValidationError as e:
                form.add_error('tel',e.message)
                return render(request,'need/add.html',{'form':form})
        
        return redirect('/user/profile')
    else:
        if request.user != None:
            form = AddNeedForm(user = request.user)
        else:
            form = AddNeedForm()
    return render(request,'need/add.html',{'form':form})

def search_view(request):
    name = request.GET.get('name')
    needs = Need.publish.filter(name__icontains=name)
    get_month_name(needs)
    paginator = Paginator(needs,25)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    kinds = list(Kind.objects.all())


    current = page.number
    total = paginator.num_pages
    start = max(current - 3, 1)
    end = min(current + 3, total) + 1
    page_range = range(start, end)

    return render(request,'need/list.html',{'needs':page,'page_range':page_range,'page_obj':page,'kinds':kinds,'len':len(needs)})