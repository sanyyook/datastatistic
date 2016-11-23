from django.shortcuts import render, redirect, reverse
from django.http.response import HttpResponse, Http404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from getterdata import GetterData
from .forms import MyAuthForm, ChangeDate
from django.core.cache import cache
# Create your views here.




def auth_user(request):
    args = {}

    if request.method == "POST":
        auth_form = MyAuthForm(request.POST)
        if auth_form.is_valid():
            print(auth_form.cleaned_data['login'])
            print(auth_form.cleaned_data['password'])
            data = GetterData(auth_form.cleaned_data['login'], auth_form.cleaned_data['password'])
            if data.client_info:
                request.session['login'] = auth_form.cleaned_data['login']
                request.session['password'] = auth_form.cleaned_data['password']
                return redirect('/')
            else:
                args['error'] = True
    args['form'] = MyAuthForm()
    return render(request, 'main/auth_user.html', args)



def logout(request):
    del request.session['login']
    del request.session['password']
    cache.clear()
    return redirect('/')



def get_sale_data(request, page_number=1, up=False):
    if 'login' in request.session:
        data = GetterData(request.session.get('login'), request.session.get('password'))
        if data.client_info:
            args = {}
            args['user'] = data.client_info
            change = ChangeDate(request.GET)
            if change.is_valid():
                args['change_date'] = change
                args['data'] = data.get_sale_info(change.cleaned_data['date_from'], change.cleaned_data['date_to'], up, int(page_number))
                paginator = Paginator(range(0, data.sale_info_len), data.count_on_page)
                try:
                    args['pages'] = paginator.page(page_number)
                except Exception:
                    args['data'] = None
                args['get'] = "date_from={}&date_to={}".format(change.cleaned_data['date_from'], change.cleaned_data['date_to'])
            else:
                args['change_date'] = ChangeDate()

            if up:
                return render(request, 'main/self_info_down.html', args)
            else:
                return render(request, 'main/sale_info.html', args)

    return render(request, 'main/none_user.html')


def get_sale_info_down(request, page_number=1):
    return get_sale_data(request, page_number, True )


def get_sale_info(request, page_number=1):
    return get_sale_data(request, page_number, False)



def main_factors(request):
    if 'login' in request.session:
        data = GetterData(request.session.get('login'), request.session.get('password'))
        if data.client_info:
            args = {}
            args['user'] = data.client_info
            change = ChangeDate(request.GET)
            if change.is_valid():
                args['change_date'] = change
                args['main_factors'] = data.getMainFactors(change.cleaned_data['date_from'], change.cleaned_data['date_to'])
            else:
                args['change_date'] = ChangeDate()
            return render(request, 'main/main_factors.html', args)

    return render(request, 'main/none_user.html')



def main(request):
    if 'login' in request.session:
        data = GetterData(request.session.get('login'), request.session.get('password'))
        if data.client_info:
            args = {}
            args['user'] = data.client_info
            return render(request, 'main/change_block.html', args)

    return render(request, 'main/none_user.html')

