from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


def home(request):
    try:
        is_logged = request.session['is_logged']
    except KeyError as err:
        return render(request, 'accounts/index.html')

    template_name = 'home/home.html'
    template = loader.get_template(template_name)
    context = {
        'page_title': 'Home',
    }
    return HttpResponse(template.render(context, request))


def about(request):
    try:
        is_logged = request.session['is_logged']
    except KeyError as err:
        return render(request, 'accounts/index.html')

    return render(request, 'home/about.html')


def contact(request):
    try:
        is_logged = request.session['is_logged']
    except KeyError as err:
        return render(request, 'accounts/index.html')

    return render(request, 'home/contact.html')


def team(request):
    try:
        is_logged = request.session['is_logged']
    except KeyError as err:
        return render(request, 'accounts/index.html')

    return render(request, 'home/team.html')
