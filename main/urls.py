from django.conf.urls import url, include
import views

urlpatterns = [

    url(r'^logout/', views.logout, name='logout'),
    url(r'^auth/', views.auth_user, name='login'),
    url(r'^factors/', views.main_factors, name='factors'),
    url(r'^saleinfo/up/page/(?P<page_number>\d+)/$', views.get_sale_info, name='saleinfo_page'),
    url(r'^saleinfo/down/page/(?P<page_number>\d+)/$', views.get_sale_info_down, name='saleinfo_page_down'),
    url(r'^saleinfo/up', views.get_sale_info, name='saleinfo'),
    url(r'^saleinfo/down', views.get_sale_info_down, name='saleinfo_down'),
    url(r'^', views.main, name='main'),
]