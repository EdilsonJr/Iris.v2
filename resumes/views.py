from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Resume
from django.core.validators import validate_email
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse


def resumes(request):
    try:
        is_logged = request.session['is_logged']
    except KeyError as err:
        return render(request, 'accounts/index.html')

    curriculos = Resume.objects.all()
    return render(request, 'resumes/resumes.html', {
        'curriculos': curriculos
    })


def register_resume(request):
    try:
        is_logged = request.session['is_logged']
    except KeyError as err:
        return render(request, 'accounts/index.html')

    if request.method != 'POST':
        return render(request, 'resumes/register_resume.html')

    fullname = request.POST.get('fullname')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    job_title = request.POST.get('job_title')
    pdf = request.FILES['pdf']



    # if not fullname or not email or not phone or not key_word or not email or not file:
    #     # messages.error(request, 'Nenhum campo pode estar vazio.')
    #     print('Nenhum campo pode estar vazio')
    #     return render(request, 'resumes/register_resume.html')
    #
    # # Validador de email
    # try:
    #     validate_email(email)
    # except:
    #     # messages.error(request, 'Email inválido')
    #     print('Email inválido')
    #     return render(request, 'resumes/register_resume.html')
    #
    # # Verificação de email
    # if Resume.objects.filter(email=email).exists():
    #     # messages.error(request, 'Email já cadastrado.  ')
    #     print("erro ja cadastrado")
    #     return render(request, 'resumes/register_resume.html')

    resume = Resume()
    resume.fullname = fullname
    resume.email = email
    resume.phone = phone
    resume.job_title = job_title
    resume.pdf = pdf

    resume.save()

    return HttpResponseRedirect(reverse('home'))



