from django.shortcuts import render,redirect, get_object_or_404
from .models import Need,Kind, Offer
from .forms import AddNeedForm, OfferForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.paginator import Paginator
from django.contrib.auth import login
from appuser.models import AppUser,Role
from django.template.defaultfilters import slugify
from django.http import StreamingHttpResponse
import csv
from .forms import NeedImportForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.dateparse import parse_datetime, parse_date
from django.contrib import messages

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

@login_required
def offer_view(request, need_id):
    need = get_object_or_404(Need, id=need_id, status='publish')
    
    # Check if user is trying to donate to their own need
    if need.needy == request.user:
        messages.error(request, 'Kendi ihtiyacınıza bağış yapamazsınız.')
        return redirect('/')
    
    # Check if need already has a pending offer
    if need.has_pending_offer():
        messages.error(request, 'Bu ihtiyaç için zaten bekleyen bir teklif var.')
        return redirect('/')
    
    if request.method == 'POST':
        form = OfferForm(request.POST, user=request.user)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.need = need
            offer.donor = request.user
            offer.save()
            
            # Update need status
            need.status = 'donor_find'
            need.donor = request.user
            need.save()
            
            messages.success(request, 'Bağış teklifiniz başarıyla gönderildi!')
            return redirect('/')
    else:
        form = OfferForm(user=request.user)
    
    return render(request, 'need/offer.html', {'form': form, 'need': need})

@login_required
def mark_received_view(request, need_id):
    need = get_object_or_404(Need, id=need_id, needy=request.user)
    
    if need.status == 'donor_find' and need.has_pending_offer():
        offer = need.get_pending_offer()
        offer.status = 'completed'
        offer.save()
        
        need.status = 'complated'
        need.save()
        
        messages.success(request, 'İhtiyacınız tamamlandı olarak işaretlendi!')
    else:
        messages.error(request, 'Bu işlem gerçekleştirilemedi.')
    
    return redirect('/user/profile')

#ismail
def is_admin(user):
    return user.is_staff or user.is_superuser

def export_offers(request):
    if not request.user.is_authenticated:
        return render(request,"need/unauthorized.html",{"path":"/user/login"})
    if Role.objects.filter(name="User").contains(AppUser.objects.get(user=request.user).all_values()['role']):
        return render(request,"need/unauthorized.html",{"path":"/user/login"})

    header = ['id', 'need_id', 'donor_name', 'status', 'created_at']
    rows = Offer.objects.values_list('id', 'need_id', 'donor__username', 'status', 'created')
    def row_gen():
        yield ','.join(header) + '\n'
        for row in rows:
            yield ','.join(str(item) for item in row) + '\n'

    resp = StreamingHttpResponse(row_gen(), content_type="text/csv")
    resp['Content-Disposition'] = 'attachment; filename="offers.csv"'
    return resp

def export_needs(request):
    if not request.user.is_authenticated:
        return render(request,"need/unauthorized.html",{"path":"/user/login"})
    if Role.objects.filter(name="User").contains(AppUser.objects.get(user=request.user).all_values()['role']):
        return render(request,"need/unauthorized.html",{"path":"/user/login"})

    header = ['id', 'name', 'note', 'status', 'created_at']
    rows = Need.objects.values_list('id', 'name', 'note', 'status', 'created')
    def row_gen():
        yield ','.join(header) + '\n'
        for row in rows:
            yield ','.join(str(item) for item in row) + '\n'

    resp = StreamingHttpResponse(row_gen(), content_type="text/csv")
    resp['Content-Disposition'] = 'attachment; filename="needs.csv"'
    return resp

def import_needs(request):
    if not request.user.is_authenticated:
        return render(request,"need/unauthorized.html",{"path":"/user/login"})
    if Role.objects.filter(name="User").contains(AppUser.objects.get(user=request.user).all_values()['role']):
        return render(request,"need/unauthorized.html",{"path":"/user/login"})

    if request.method == "POST":
        form = NeedImportForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['csv_file']
            decoded = f.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded)

            # Model alan isimleri listesi (id ve auto-added alanlar hariç)
            field_names = {
                f.name: f
                for f in Need._meta.get_fields()
                if getattr(f, 'editable', False) and not f.auto_created
            }

            for row in reader:
                need = Need()
                for col, val in row.items():
                    # CSV'deki başlık modeldeki bir alanla birebir eşleşiyorsa ata
                    if col in field_names and val != '':
                        field = field_names[col]
                        # Tarih/zaman alanıysa parse et
                        if field.get_internal_type() in ('DateTimeField', 'DateField'):
                            parsed = (parse_datetime(val) if field.get_internal_type()=='DateTimeField' 
                                      else parse_date(val))
                            setattr(need, col, parsed)
                        else:
                            setattr(need, col, val)
                need.save()

            return redirect('need:list')
    else:
        form = NeedImportForm()

    return render(request, 'need/import.html', {'form': form})