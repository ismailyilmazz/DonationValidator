from django.shortcuts import render,redirect
from .models import Need,Kind
from .forms import AddNeedForm
from django.contrib.auth.models import User
# Create your views here.

def list_view(request):
    needs = Need.publish.all()
    return render(request,'need/list.html',{'needs':needs,'len':len(needs)})

def add_view(request):
    if request.method == "POST":
        form = AddNeedForm(request.POST)
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        name = request.POST.get('name')
        kind = request.POST.get('kind')
        kind = Kind.objects.get(id=kind)
        needy= User.objects.get(id=1)
        tel = request.POST.get('tel')
        # try:
        need = Need(latitude=latitude,longitude=longitude,name=name,kind=kind,needy=needy)
        need.save()
        return redirect('/')
        # except:
        #     pass
    else:
        form = AddNeedForm()
    return render(request,'need/add.html',{'form':form})