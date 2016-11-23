# -*- coding: utf-8 -*-

from django import forms

class MyAuthForm(forms.Form):
    login = forms.CharField(label='Логин', max_length=100)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)



class ChangeDate(forms.Form):
    date_from = forms.DateField(label='Дата 1')
    date_to = forms.DateField(label='Дата 2')



