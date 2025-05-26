from django.shortcuts import render,redirect, get_object_or_404
from .models import Need,Kind, Offer
from .forms import AddNeedForm, OfferForm, RoleForm,DeliveryForm,BulkCourierForm,CourierWithdrawForm,DeliveryCodeForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.paginator import Paginator
from django.contrib.auth import login
from appuser.models import AppUser,Role
from django.template.defaultfilters import slugify
from django.http import StreamingHttpResponse
import csv
from .forms import NeedImportForm,KindForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.dateparse import parse_datetime, parse_date
from django.contrib import messages
from .utils import permission_required
from django.utils.timezone import now, timedelta
import random
from django.utils.encoding import smart_str
from django.db.models import Q
from datetime import datetime, timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your views here.

def get_month_name(needs):
    months = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
    for need in needs:
        need.month_name = months[need.created.month-1]

        
def detail_view(request, year, month, day, slug):
    try:
        need = Need.objects.get(created__year=year, created__month=month, created__day=day, slug=slug)
        offer = Offer.objects.filter(need=need).first()
        form = DeliveryForm()
        code_form = None

        if request.user.is_authenticated:
            appuser = AppUser.objects.get(user=request.user).all_values()
            show_form = False

            # Kod formu gösterme koşulu:
            if offer and offer.courier == request.user and offer.code:
                code_form = DeliveryCodeForm(request.POST or None)

                if request.method == 'POST' and 'code' in request.POST:
                    code_form = DeliveryCodeForm(request.POST)
                    if code_form.is_valid():
                        input_code = code_form.cleaned_data['code']
                        if input_code == offer.code:
                            need.status = 'completed'
                            need.save()
                            offer.status = 'completed'
                            offer.save()
                            messages.success(request, "Teslimat başarıyla tamamlandı.")
                            return redirect(need.get_absolute_url())
                        else:
                            messages.error(request, "Geçersiz kod. Lütfen kontrol edin.")

            # Teslimat seçimi formu (self / courier)
            if need.donor == request.user and need.status == 'donor_find':
                show_form = True
                form = DeliveryForm(request.POST or None)
                if request.method == 'POST' and 'delivery_method' in request.POST:
                    form = DeliveryForm(request.POST)
                    if form.is_valid():
                        delivery_method = form.cleaned_data['delivery_method']
                        if delivery_method == 'self':
                            need.status = 'transportation'
                            offer.courier = request.user
                            need.save()
                            offer.save()
                            messages.success(request, "Teslimat kendiniz tarafından yapılacak olarak işaretlendi.")
                        elif delivery_method == 'courier':
                            need.status = 'courier_request'
                            need.save()
                            messages.success(request, "Kurye talebiniz iletildi.")
                        return redirect(need.get_absolute_url())

            return render(request, 'need/detail.html', {
                'need': need,
                'offer': offer,
                'form': form,
                'code_form': code_form,
                'show_form': show_form,
                'appuser': appuser,
            })

        else:
            return render(request, 'need/detail.html', {
                'need': need,
                'offer': offer,
                'form': None,
                'code_form': None,
                'show_form': False,
                'appuser': None,
            })

    except ObjectDoesNotExist:
        return render(request, 'need/detail.html', {'need': None})

@login_required
def generate_code(request, year, month, day, slug):
    need = get_object_or_404(Need, created__year=year, created__month=month, created__day=day, slug=slug)
    offer = get_object_or_404(Offer, need=need)

    if request.user != offer.courier:
        messages.error(request, "Bu işlemi yapma yetkiniz yok.")
        return redirect(need.get_absolute_url())

    if need.status != 'transportation':
        messages.error(request, "Kod sadece taşımada olan ihtiyaçlar için oluşturulabilir.")
        return redirect(need.get_absolute_url())

    # Kod oluştur
    import random
    code = str(random.randint(100000, 999999))
    offer.code = code
    offer.save()
    messages.success(request, f"Teslimat Kodu Oluşturuldu")

    return redirect(need.get_absolute_url())


def delete_need(request,year,month,day,slug):
    try:
        if request.user.is_authenticated:
            need = Need.objects.get(created__year=year,created__month=month,created__day=day,slug=slug)
            userPermissions = AppUser.objects.get(user=request.user).all_values()["permissions"]
            if need.needy == request.user or "need_delete" in userPermissions:
                need.delete()
        return redirect("/")        
    except ObjectDoesNotExist:
            return redirect("/")
    


def list_view(request):
    needs = Need.publish.all()
    query = request.GET.get('q', '')
    kind_slug = request.GET.get('kind')
    date_filter = request.GET.get('date')

    if query:
        needs = needs.filter(name__icontains=query)

    kind_list = request.GET.getlist('kind')

    if kind_list:
        needs = needs.filter(kind__slug__in=kind_list)

    if date_filter == 'today':
        needs = needs.filter(created__date=now().date())
    elif date_filter == '2days':
        needs = needs.filter(created__date__gte=now().date() - timedelta(days=2))
    elif date_filter == 'week':
        needs = needs.filter(created__date__gte=now().date() - timedelta(days=7))

    get_month_name(needs) 
    paginator = Paginator(needs, 25)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    kinds = Kind.objects.all()

    current = page.number
    total = paginator.num_pages
    start = max(current - 3, 1)
    end = min(current + 3, total) + 1
    page_range = range(start, end)

    appuser = None
    if request.user.is_authenticated:
        appuser = AppUser.objects.get(user=request.user).all_values()

    return render(request, 'need/list.html', {
        'needs': page,
        'page_range': page_range,
        'page_obj': page,
        'kinds': kinds,
        'kind_list':kind_list,
        'appuser': appuser,
        'len': len(needs),
        'query': query,
        'date_filter': date_filter,
        'kind_slug': kind_slug,
    })



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
        address = request.POST.get('address')
        latitude = latitude if latitude else 0
        longitude = longitude if longitude else 0
        if request.user.is_authenticated:
            needy = User.objects.get(username = request.user.username)
            appuser=AppUser.objects.get(user=needy)
            all_values = appuser.all_values()
            if len(all_values["address"]) == 0: 
                appuser.address = [address]
                appuser.current_address = 0                
            elif all_values["address"][all_values["current_address"]] != address:
                new_address_list = all_values["address"] + [address]
                print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", new_address_list)
                appuser.address = new_address_list
                appuser.current_address = len(new_address_list) - 1
            appuser.save()

            need = Need(latitude=latitude,longitude=longitude,name=name,kind=kind,needy=needy,address=address)
            need.save()
        else:
            tel = request.POST.get('tel')
            try:
                add_control(tel=tel)
                try:
                    role = Role.objects.get(slug="user")
                except Role.DoesNotExist:
                    role = Role(name="User", slug="user")
                    role.save()
                user = User(username=create_username(firstname=first_name),password=tel,first_name=first_name,last_name=last_name)
                user.save()
                AppUser.objects.create(tel=tel,
                                       user=user,
                                       role=role,
                                       address=[address] if address else [],
                                        current_address=0 if address else -1,)
                login(request=request,user=user)
                need = Need(latitude=latitude,longitude=longitude,name=name,kind=kind,needy=user,address=address)
                need.save()
            except ValidationError as e:
                form.add_error('tel',e.message)
                return render(request,'need/add.html',{'form':form})
            

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            "global_chat",
            {
                "type": "new_need_added",
                "need": {
                    "name": need.name,
                    "kind": need.kind.name,
                    "created": str(need.created),
                    "slug": need.slug,
                    "pk": need.pk,
                    "url": need.get_absolute_url(),
                }
            }
        )
            
        
        return redirect('/user/profile')
    else:
        if request.user != None:
            form = AddNeedForm(user = request.user)
        else:
            form = AddNeedForm()
    return render(request,'need/add.html',{'form':form})

################ COURIER ######################


@login_required
def courier_request_list(request):
    appuser = AppUser.objects.get(user=request.user).all_values()
    if 'offer_update' not in appuser['permissions']:
        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
        return redirect('/unauthorized')

    needs = Need.objects.filter(status='courier_request').order_by('-id')
    query = request.GET.get('q')
    if query:
        needs = needs.filter(address__icontains=query)

    paginator = Paginator(needs, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = BulkCourierForm(needs_queryset=page_obj.object_list)

    if request.method == 'POST':
        form = BulkCourierForm(request.POST, needs_queryset=needs)
        if form.is_valid():
            ids = form.cleaned_data['needs']
            needs = Need.objects.filter(id__in=ids)
            for need in needs:
                need.status = "transportation"
                offer = Offer.objects.get(need=need)
                offer.courier = request.user
                need.save()
                offer.save()

            messages.success(request, f"Başarıyla atandı.")
            return redirect(request.path)
    if query == None:
        query=''

    return render(request, 'courier/courier_list.html', {
        'page_obj': page_obj,
        'form': form,
        'query': query
    })


@login_required
def my_courier_needs(request):
    appuser = AppUser.objects.get(user=request.user).all_values()
    if 'offer_update' not in appuser['permissions']:
        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
        return redirect('/unauthorized')

    needs = Need.objects.filter(offers__courier=request.user).order_by('-id')
    query = request.GET.get('q')
    if query:
        needs = needs.filter(address__icontains=query)

    paginator = Paginator(needs, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = CourierWithdrawForm(needs_queryset=page_obj.object_list)

    if request.method == 'POST':
        form = CourierWithdrawForm(request.POST, needs_queryset=needs)
        if form.is_valid():
            ids = form.cleaned_data['needs']
            for need in Need.objects.filter(id__in=ids):
                offer = Offer.objects.get(need=need)
                offer.courier = None
                need.status = 'courier_request'
                offer.save()
                need.save()
            messages.success(request, "Seçilen ihtiyaçlardan taşıyıcılıktan çekildiniz.")
            return redirect(request.path)
    if query == None:
        query=''
    return render(request, 'courier/my_courier_needs.html', {'form': form, 'page_obj': page_obj, 'query': query})


#################################################


############## KIND  ##########################33#

def kind_list(request):
    if not request.user.is_authenticated:
        return render(request,'need/unauthorized.html')
    appuser = AppUser.objects.get(user=request.user).all_values()
    if "category" not in appuser["permissions"]:
        return render(request,'need/unauthorized.html')
    
    kinds = Kind.objects.all()
    form = KindForm()

    if request.method == 'POST':
        form = KindForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('need:kind_list') 

    return render(request, 'need/kind_list.html', {'kinds': kinds, 'form': form})


def kind_update(request, slug):
    if not request.user.is_authenticated:
        return render(request,'need/unauthorized.html')
    appuser = AppUser.objects.get(user=request.user).all_values()
    if "category" not in appuser["permissions"]:
        return render(request,'need/unauthorized.html')
    
    kind = get_object_or_404(Kind, slug=slug)
    if request.method == 'POST':
        form = KindForm(request.POST, instance=kind)
        if form.is_valid():
            form.save()
            return redirect('need:kind_list')
    else:
        form = KindForm(instance=kind)
    return render(request, 'need/kind_form.html', {'form': form})



def kind_delete(request, slug):
    if not request.user.is_authenticated:
        return render(request, 'need/unauthorized.html')
    
    appuser = AppUser.objects.get(user=request.user).all_values()
    if "category" not in appuser["permissions"]:
        return render(request, 'need/unauthorized.html')
    
    kind = get_object_or_404(Kind, slug=slug)
    linked_needs = Need.objects.filter(kind=kind)

    if linked_needs.exists():
        messages.error(request, f"Bu kategoriyi silemezsiniz. '{kind.name}' kategorisine bağlı ihtiyaçlar mevcut.")
        return redirect('need:kind_list')

    if request.method == 'POST':
        kind.delete()
        messages.success(request, f"{kind.name} başarıyla silindi.")
        return redirect('need:kind_list')

    return render(request, 'need/kind_confirm_delete.html', {'kind': kind})


########################################


############## ROLE #####################




@permission_required('role_add')
def role_create(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('need:role_list')
    else:
        form = RoleForm()
    return render(request, 'role/role_form.html', {'form': form})

@permission_required('role_update')
def role_update(request, slug):
    role = get_object_or_404(Role, slug=slug)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            return redirect('need:role_list')
    else:
        form = RoleForm(instance=role)
    return render(request, 'role/role_form.html', {'form': form})

@permission_required('role_add')
def role_list(request):
    roles = Role.objects.all()
    permissions = Role.PERMISSION_CHOICES
    return render(request, 'role/role_list.html', {'roles': roles, 'permissions': permissions})


@permission_required('role_delete')
def role_delete(request, slug):
    role = get_object_or_404(Role, slug=slug)

    if AppUser.objects.filter(role=role).exists():
        messages.error(request, f"{role.name} adlı rol, kullanıcılar tarafından kullanıldığı için silinemez.")
        return redirect('need:role_list')

    role.delete()
    messages.success(request, f"{role.name} adlı rol başarıyla silindi.")
    return redirect('need:role_list')



#######################################

def unauthorized_view(request):
    return render(request,'need/unauthorized.html')



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


########## IMOPORT EXPORT ########################


# def export_offers(request):
#     if not request.user.is_authenticated:
#         return render(request,"need/unauthorized.html",{"path":"/user/login"})
#     if Role.objects.filter(name="User").contains(AppUser.objects.get(user=request.user).all_values()['role']):
#         return render(request,"need/unauthorized.html",{"path":"/user/login"})

#     header = ['id', 'need_id', 'donor_name', 'status', 'created_at']
#     rows = Offer.objects.values_list('id', 'need_id', 'donor__username', 'status', 'created')
#     def row_gen():
#         yield '\ufeff' + ','.join(header) + '\n'
#         for row in rows:
#             yield ','.join(str(item) for item in row) + '\n'

#     resp = StreamingHttpResponse(row_gen(), content_type="text/csv; charset=utf-8")
#     resp['Content-Disposition'] = 'attachment; filename="offers.csv"'
#     return resp

@login_required
@permission_required('data_export')
def export_needs(request):
    query = request.GET.get('q', '')
    kind_filter = request.GET.getlist('kind')
    status_filter = request.GET.get('status')

    needs = Need.objects.all()

    if query:
        needs = needs.filter(Q(name__icontains=query) | Q(note__icontains=query) | Q(address__icontains=query))
    if kind_filter:
        needs = needs.filter(kind__slug__in=kind_filter)
    if status_filter:
        needs = needs.filter(status=status_filter)

    header = ['İsim', 'Kategori', 'Not', 'Adres', 'Durum', 'Tarih']
    rows = needs.values_list('name', 'kind__name', 'note', 'address', 'status', 'created')

    def row_gen():
        yield '\ufeff' + ','.join(header) + '\n'
        for row in rows:
            row = [smart_str(item).replace('\n', ' ').replace(',', ' ') for item in row]
            yield ','.join(row) + '\n'

    resp = StreamingHttpResponse(row_gen(), content_type="text/csv; charset=utf-8")
    resp['Content-Disposition'] = 'attachment; filename="needs.csv"'
    return resp



@login_required
@permission_required('data_import')
def import_needs(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, "Dosya yüklenmedi.")
            return redirect('need:import_needs')

        decoded = csv_file.read().decode('utf-8-sig').splitlines()
        reader = csv.DictReader(decoded)

        # Sadece name, address, kind alınacak
        preview_list = []
        for row in reader:
            preview_list.append({
                'name': row.get('name', '').strip(),
                'address': row.get('address', '').strip(),
                'kind': row.get('kind', '').strip(),
            })

        request.session['imported_needs'] = preview_list
        return redirect('need:import_confirm')

    return render(request, 'import_export/import_needs.html')

@login_required
@permission_required('data_import')
def import_confirm(request):
    needs = request.session.get('imported_needs', [])
    kinds = Kind.objects.all()  # Kategori listesi

    if request.method == 'POST':
        if 'delete' in request.POST:
            index = int(request.POST['delete'])
            if index < len(needs):
                needs.pop(index)
                request.session['imported_needs'] = needs
                messages.success(request, "Seçilen satır silindi.")
            return redirect('need:import_confirm')

        elif 'confirm' in request.POST:
            for i, data in enumerate(needs):
                name = request.POST.get(f'name_{i}', data['name'])
                address = request.POST.get(f'address_{i}', data['address'])
                kind_name = request.POST.get(f'kind_{i}', data['kind'])
                try:
                    kind = Kind.objects.get(name=kind_name)
                except Kind.DoesNotExist:
                    messages.error(request, f"{name} için kategori bulunamadı.")
                    continue

                Need.objects.create(
                    name=name,
                    address=address,
                    kind=kind,
                    needy=request.user,                    
                )

            del request.session['imported_needs']
            messages.success(request, "İhtiyaçlar başarıyla eklendi.")
            return redirect('need:needs_list')

    return render(request, 'import_export/import_confirm.html', {'needs': needs, 'kinds': kinds})



@login_required
@permission_required('data_export')
def import_export_dashboard(request):
    needs = Need.objects.exclude(status='completed')

    # Filtreleme
    name_query = request.GET.get('name', '')
    if name_query:
        needs = needs.filter(name__icontains=name_query)

    kinds = request.GET.getlist('kind')
    if kinds:
        needs = needs.filter(kind__slug__in=kinds)

    status_query = request.GET.get('status', '')
    if status_query:
        needs = needs.filter(status=status_query)

    date_filter = request.GET.get('date', '')
    now = datetime.now()

    if date_filter == 'today':
        needs = needs.filter(created__date=now.date())
    elif date_filter == 'last_2_days':
        needs = needs.filter(created__gte=now - timedelta(days=2))
    elif date_filter == 'last_week':
        needs = needs.filter(created__gte=now - timedelta(weeks=1))
    elif date_filter == 'last_month':
        needs = needs.filter(created__gte=now - timedelta(days=30))

    # Paginator
    paginator = Paginator(needs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Export
    if request.GET.get('export') == 'csv':
        header = ['name', 'kind', 'note', 'status', 'address', 'created_at']
        rows = needs.values_list('name', 'kind__name', 'note', 'status', 'address', 'created')

        def row_gen():
            yield '\ufeff' + ','.join(header) + '\n'
            for row in rows:
                row = [str(item).replace('\n', ', ').replace('\r', '') for item in row]
                yield ','.join(row) + '\n'

        resp = StreamingHttpResponse(row_gen(), content_type="text/csv; charset=utf-8")
        resp['Content-Disposition'] = 'attachment; filename="needs.csv"'
        return resp

    kinds_list = Kind.objects.all()
    return render(
        request,
        'import_export/import_export_dashboard.html',
        {
            'needs': page_obj,
            'selected_kinds': kinds,
            'kinds': kinds_list,
            'page_obj': page_obj,
        }
    )




##################################