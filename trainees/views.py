from .serializers import registrationSerializers
from .models import Registration, Trainee
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from datetime import date


def register_view(request):
    if request.method == 'POST':
        Registration.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            national_id=request.POST.get('national_id'),
            documnts=request.POST.get('documnts')
        )
        messages.success(request, "done")
        return redirect('registration')
    return render(request, 'registration.html')


def end_training_view(request, id):
    trainee_obj = get_object_or_404(Trainee, id=id)
    if request.method == 'POST':
        trainee_obj.status = 'منتهي'
        trainee_obj.save()
        messages.success(request, f"تم اعتماد إنهاء تدريب {trainee_obj.name} ✅")
        return redirect('/admin/trainees/trainee/')
    context = {
        'trainee': trainee_obj,
        'date': date.today(),
    }
    return render(request, 'admin/test1.html', context)