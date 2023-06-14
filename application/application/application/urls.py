"""application URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from gascom import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index),
    path('login/login_staff/',views.login_staff),
    path('login/login_supplier/',views.login_supplier), 
    path('register/successfully_register/',views.successfully_register),
    path('<int:staff_id>/view_staff/',views.view_staff),
    path('<int:supplier_id>/view_supplier/',views.view_supplier),
    path('<int:staff_id>/home_staff/',views.home_staff),
    path('<int:supplier_id>/home_supplier/',views.home_supplier),
    path('<int:staff_id>/supplier_operate/',views.supplier_operate),
    path('<int:staff_id>/deliery_operate/',views.deliery_operate),
    path('<int:staff_id>/gas_in_operate/',views.gas_in_operate),
    path('<int:staff_id>/gas_operate/',views.gas_operate),
    path('register/register_customer/',views.register_customer),
    path('login/login_customer/',views.login_customer),
    path('<int:customer_pho>/view_customer/',views.customer_operate),
    path('<int:customer_pho>/home_customer/',views.home_customer),
 
    path('<int:staff_id>/deliery_search/',views.deliery_search),
    path('<int:staff_id>/gas_out_operate/',views.gas_out_operate),
    path('<int:deliery_id>/view_deliery/',views.view_deliery),
    
    # path('')
]
