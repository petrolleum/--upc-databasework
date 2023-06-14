import requests
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from . import forms
from . import models
import json
from django.http import JsonResponse
from django.db import transaction
from django.contrib import auth,sessions
from django.contrib.auth.models import User
import datetime
from django.db.models import Max,Sum
from django.db.models import Count
from django.db.models.functions import Coalesce
from django.db.models.functions import Cast

from django.db.models import Func, IntegerField
import calendar
# Create your views here.
def index(request):
    return render(request, 'home.html')
def staff_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('staff_id'):  # 假设使用session来存储用户ID
            return redirect('../../login/login_staff')  # 未登录用户重定向到登录页面
        return view_func(request, *args, **kwargs)
    return wrapper
def customer_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('customer_id'):  # 假设使用session来存储用户ID
            return redirect('../../login/login_customer')  # 未登录用户重定向到登录页面
        return view_func(request, *args, **kwargs)
    return wrapper
def login_staff(request):
    if(request.method=='GET'):
        return render(request,'login/login_staff.html')
    elif(request.method=='POST'):
       test_forms=forms.Login_staff(request.POST)
       if test_forms.is_valid():
           staff_id=test_forms.cleaned_data.get('staff_id')
           password=test_forms.cleaned_data.get('password')
           print(staff_id)
           print(password)
           
           if models.Staff.objects.filter(num=staff_id,password=password).exists():
               request.session['staff_id']=staff_id
               return redirect("../../"+staff_id+"/view_staff/")
           else:
               return render(request,'login/login_staff.html',{'errorname':'用户名或密码错误'})

def login_customer(request):
    if(request.method=='GET'):
        return render(request,'login/login_customer.html')
    elif(request.method=='POST'):
       test_forms=forms.Login_customer(request.POST)
       if test_forms.is_valid():
           customer_id=test_forms.cleaned_data.get('customer_id')
           password=test_forms.cleaned_data.get('password')
           
           all_data=models.Customer.objects.all()
           if models.Customer.objects.filter(phonenum=customer_id,password=password).exists():
               request.session['customer_id']=customer_id
               return redirect("../../"+customer_id+"/view_customer/")
           else:
               return render(request,'login/login_customer.html',{'errorname':'用户名或密码错误'})
           
def login_supplier(request):
    if(request.method=='GET'):
        return render(request,'login/login_supplier.html')
    elif(request.method=='POST'):
       test_forms=forms.Login_supplier(request.POST)
       if test_forms.is_valid():
           supplier_id=test_forms.cleaned_data.get('supplier_id')
           password=test_forms.cleaned_data.get('password')
           all_data=models.Supplier.objects.all()
           if models.Customer.objects.filter(num=supplier_id,password=password).exists():
               return redirect("../../"+supplier_id+"/view_supplier/")
           else:
               return render(request,'login/login_supplier.html',{'errorname':'用户名或密码错误'})

def register_customer(request):
    if(request.method=='GET'):
        return render(request,'register/register_customer.html')
    elif(request.method=='POST'):
        test_form=forms.Register(request.POST)
        if test_form.is_valid():
            try:
                name=test_form.cleaned_data.get('name')
                phonenum=test_form.cleaned_data.get('phonenum')
                address=test_form.cleaned_data.get('address')
                password=test_form.cleaned_data.get('password')
                result=models.Customer.objects.create(name=name,phonenum=phonenum,address=address,password=password)
                result.save()
                return redirect("../successfully_register")     
            except Exception as e:
                print(str(e))
                render(request,'register/register_customer.html',{"errorname":"注册失败"})
        else:
            return render(request,'register/register_customer.html',{'errorname':'表单接收错误'})
def successfully_register(request):
    return render(request,'register/successfully_register.html')
def view_customer(request,customer_pho):
    name=models.Customer.objects.get(phonenum=customer_pho).name
    gas_list=models.Gas_category.objects.all()
    context={'customer_name':name,'gas_list':gas_list}
    return render(request,'view/view_customer.html',context)
@staff_login_required
def view_staff(request,staff_id):
    x_list1=[]
    y_list1=[]
    is_in_gas_out=[]
    deliery_amount = models.Deliery_gas.objects.values('deliery_id').annotate(total_amount=Coalesce(Sum('gas_out_id__amount'), 0))
    deliery_list=models.Deliery_staff.objects.all()
    for i in deliery_amount:
        a=models.Deliery_staff.objects.get(num=i['deliery_id']).num
        is_in_gas_out.append(a)
    for deliery in deliery_list:
        x_list1.append(deliery.num)
        if deliery.num in is_in_gas_out:
            for i in deliery_amount:
                if deliery.num==i["deliery_id"]:
                    y_list1.append(i["total_amount"])
                    break
        else:
            y_list1.append(0)
    sorted_data1 = sorted(zip(x_list1, y_list1), key=lambda x: x[1],reverse=True)
    x_list1 = [x for x, _ in sorted_data1]
    y_list1 = [y for _, y in sorted_data1]
    x_list1=x_list1[0:10]
    y_list1=y_list1[0:10]
    # 以上是所有配送员配送总量的数据
    sum_amount=models.Gas_out.objects.values('customer_pho').annotate(sum_amount=Sum('amount'))
    print(sum_amount)
    x_list=[]
    y_list=[]
    for i in sum_amount:
        a=i['customer_pho']
        b=i['sum_amount']
        x_list.append(a)
        y_list.append(b)
    
    sorted_data = sorted(zip(x_list, y_list), key=lambda x: x[1],reverse=True)
    x_list = [x for x, _ in sorted_data]
    y_list = [y for _, y in sorted_data]
    x_list=x_list[0:10]
    y_list=y_list[0:10]
    print(x_list,y_list)
    if request.method=='GET':
        name=models.Staff.objects.get(num=staff_id).name
        gas_out_list=models.Gas_out.objects.filter(is_deliery=0)
        deliery_list=models.Deliery_staff.objects.all()
        deliery_count=deliery_list.count()
        context={'staff_name':name,'gas_out_list':gas_out_list,'deliery_list':deliery_list,'deliery_count':deliery_count,'x_list':x_list,'y_list':y_list,'x_list1':x_list1,'y_list1':y_list1}
        return render(request,'view/view_staff.html',context)
    elif request.method=='POST':
        gas_out_num=request.POST.get("gas_out_num")
        gas_out_num=int(gas_out_num)
        deliery_num=request.POST.get("deliery")
        insert_gas_out=models.Gas_out.objects.get(num=gas_out_num)
        insert_deliery=models.Deliery_staff.objects.get(num=deliery_num)
        try:
            with transaction.atomic():
                if models.Deliery_gas.objects.filter(num=1).count()<=0:
                    models.Deliery_gas.objects.create(num=1,deliery_id=insert_deliery,gas_out_id=insert_gas_out)
                else:
                    max_value=models.Deliery_gas.objects.aggregate(max_value=Max('num'))
                    insert_num=max_value['max_value']+1
                    models.Deliery_gas.objects.create(num=insert_num,deliery_id=insert_deliery,gas_out_id=insert_gas_out)
                result=models.Gas_out.objects.get(num=gas_out_num)
                result.is_deliery=1
                result.save()
            x_list1=[]
            y_list1=[]
            is_in_gas_out=[]
            deliery_amount = models.Deliery_gas.objects.values('deliery_id').annotate(total_amount=Coalesce(Sum('gas_out_id__amount'), 0))
            deliery_list=models.Deliery_staff.objects.all()
            for i in deliery_amount:
                a=models.Deliery_staff.objects.get(num=i['deliery_id']).num
                is_in_gas_out.append(a)
            for deliery in deliery_list:
                x_list1.append(deliery.num)
                if deliery.num in is_in_gas_out:
                    for i in deliery_amount:
                        if deliery.num==i["deliery_id"]:
                            y_list1.append(i["total_amount"])
                            break
                else:
                    y_list1.append(0)
            sorted_data1 = sorted(zip(x_list1, y_list1), key=lambda x: x[1],reverse=True)
            x_list1 = [x for x, _ in sorted_data1]
            y_list1 = [y for _, y in sorted_data1]
            x_list1=x_list1[0:10]
            y_list1=y_list1[0:10]
            name=models.Staff.objects.get(num=staff_id).name
            gas_out_list=models.Gas_out.objects.filter(is_deliery=0)
            deliery_list=models.Deliery_staff.objects.all()
            deliery_count=deliery_list.count()
            
            context={'success':True,'staff_name':name,'gas_out_list':gas_out_list,'deliery_list':deliery_list,'deliery_count':deliery_count,'x_list':x_list,'y_list':y_list,'x_list1':x_list1,'y_list1':y_list1}
            return render(request,"view/view_staff.html",context)
        except Exception as e:
            print({{str(e)}})
            name=models.Staff.objects.get(num=staff_id).name
            gas_out_list=models.Gas_out.objects.filter(is_deliery=0)
            deliery_list=models.Deliery_staff.objects.all()
            deliery_count=deliery_list.count()
            context={'error':True,'staff_name':name,'gas_out_list':gas_out_list,'deliery_list':deliery_list,'deliery_count':deliery_count,'x_list':x_list,'y_list':y_list,'x_list1':x_list1,'y_list1':y_list1}
            return render(request,"view/view_staff.html",context)
def view_supplier(request,supplier_id):
    name=models.Staff.objects.get(num=supplier_id).name
    context={'supplier_name':name}
    return render(request,'view/view_supplier.html',context)
def home_customer(request):
    return render(request,'view/home_customer.html')
def home_staff(request):
    return render(request,'view/home_staff.html')
def home_supplier(request):
    return render(request,'view/home_supplier.html')
@staff_login_required
def supplier_operate(request,staff_id):
    if request.method=='GET':
        # try:
        #     json_data = json.loads(request.body)
        #     print(json_data)
        #     key = json_data.get('back')
        # except json.JSONDecodeError:
        #     pass

        # if key:
        #     print(1)
        #     supplier_list=models.Supplier.objects.all()
        #     staff_name=models.Staff.objects.get(num=staff_id).name
        #     context={'success':'1','supplier_list':supplier_list,'staff_name':staff_name,}
        #     return HttpResponse("helloword ")
        length=models.Supplier.objects.count()
        supplier_list=models.Supplier.objects.all()
        staff_name=models.Staff.objects.get(num=staff_id).name
        context={'supplier_list':supplier_list,'staff_name':staff_name,'length':length}
       
        return render(request,'operate/supplier_operate.html',context)
    elif request.method=='POST':
        insert_form=forms.Insert_supplier(request.POST)
        select_form=forms. Select_supplier(request.POST)
        update_form=forms.Update(request.POST)
        delete_form=forms.Delete(request.POST)
        if insert_form.is_valid():
            supplier_id=insert_form.cleaned_data.get('supplier_id')
            name=insert_form.cleaned_data.get('name')
            phonenum=insert_form.cleaned_data.get('phonenum')
            
            try:
                models.Supplier.objects.create(num=supplier_id,name=name,phonenum=phonenum)
                supplier_list=models.Supplier.objects.all()
                staff_name=models.Staff.objects.get(num=staff_id).name
                context={'success':'1','supplier_list':supplier_list,'staff_name':staff_name,}
                return render(request,'operate/supplier_operate.html',context)
            except Exception as e:
                print({{str(e)}})
                supplier_list=models.Supplier.objects.all()
                staff_name=models.Staff.objects.get(num=staff_id).name
                context={'error':True,'supplier_list':supplier_list,'staff_name':staff_name,}
                return render(request,'operate/supplier_operate.html',context)
            
        elif select_form.is_valid():             
            selectinf=select_form.cleaned_data.get('selectinf')
            filter_inf1=models.Supplier.objects.filter(num=selectinf)
            filter_result=models.Supplier.objects.filter(name=selectinf).union(filter_inf1)
            supplier_list=models.Supplier.objects.all()
            staff_name=models.Staff.objects.get(num=staff_id).name
            context={'filter_result':filter_result,'staff_name':staff_name,'supplier_list':supplier_list}
            return render(request,'operate/supplier_operate1.html',context)
        elif request.POST.get('supplier_id'):
            supplier_id=request.POST.get('supplier_id')
            print(supplier_id)
            data=models.Supplier.objects.filter(num=supplier_id).first()
            data.delete()
            supplier_list=models.Supplier.objects.all()
            staff_name=models.Staff.objects.get(num=staff_id).name
            context={'success':'1','supplier_list':supplier_list,'staff_name':staff_name}
            return render(request,'operate/supplier_operate.html',context)
        elif request.POST.get("update_supplier_id"):
            supplier_id=request.POST.get("update_supplier_id")
            print(supplier_id)
            name=request.POST.get("name")
            phonenum=request.POST.get("phonenum")
           
            models.Supplier.objects.filter(num=supplier_id).update(num=supplier_id,name=name,phonenum=phonenum)
            
            supplier_list=models.Supplier.objects.all()
            staff_name=models.Staff.objects.get(num=staff_id).name
            context={'success':'1','supplier_list':supplier_list,'staff_name':staff_name,}
            return render(request,'operate/supplier_operate.html',context)
        # elif request.is_ajax():
        #     data=json.loads(request.body)
        #     if 'delete' in data:
        #         print("123123")
        #         supplier_id=data['supplier_id']
        #         print(type(supplier_id))
        #         list=models.Supplier.objects.get(num=supplier_id)
        #         q=list.delete
        #         print(q)
        #         supplier_list=models.Supplier.objects.all()
        #         staff_name=models.Staff.objects.get(num=staff_id).name
        #         length=models.Supplier.objects.count()
        #         context={'staff_name':staff_name,'supplier_list':supplier_list,'length':length}
        #         return render(request,'operate/supplier_operate.html',context) 
                   
        else:
            supplier_list=models.Supplier.objects.all()
            staff_name=models.Staff.objects.get(num=staff_id).name
                
            context={'errorname':'插入失败请重试！','supplier_list':supplier_list,'staff_name':staff_name}
            return render(request,'operate/supplier_operate.html',context)
@staff_login_required   
def deliery_operate(request,staff_id):
    if request.method=='GET':
        deliery_list=models.Deliery_staff.objects.all()
        staff_name=models.Staff.objects.get(num=staff_id).name
        context={'deliery_list':deliery_list,'staff_name':staff_name}
        return render(request,"operate/deliery_operate.html",context)
    elif request.method=='POST':
        if request.POST.get("insert_deliery_id"):
            deliery_id=request.POST.get("insert_deliery_id")
            name=request.POST.get("name")
            phonenum=request.POST.get("phonenum")
            staff_name=models.Staff.objects.get(num=staff_id).name
            deliery_list=models.Deliery_staff.objects.all()
            try:
                models.Deliery_staff.objects.create(num=deliery_id,name=name,phonenum=phonenum)
                deliery_list=models.Deliery_staff.objects.all()
                staff_name=models.Staff.objects.get(num=staff_id).name
                context={'success':'1','deliery_list':deliery_list,'staff_name':staff_name,}
                return render(request,'operate/deliery_operate.html',context)
            except:
                context={'error':True,'deliery_list':deliery_list,'staff_name':staff_name,}
                return render(request,'operate/deliery_operate.html',context)
            
        elif request.POST.get("selectinf"):
            selectinf=request.POST.get("selectinf")
            filter_inf1=models.Deliery_staff.objects.filter(num=selectinf)
            filter_result=models.Deliery_staff.objects.filter(name=selectinf).union(filter_inf1)           
            staff_name=models.Deliery_staff.objects.get(num=staff_id).name
            context={'filter_result':filter_result,'staff_name':staff_name}
            return render(request,'operate/deliery_operate.html',context)
        elif request.POST.get("delete_deliery_id"):
            delete_deliery_id=request.POST.get('delete_deliery_id')
            print(delete_deliery_id)
            data=models.Deliery_staff.objects.filter(num=delete_deliery_id).first()
            data.delete()
            deliery_list=models.Deliery_staff.objects.all()
            staff_name=models.Staff.objects.get(num=staff_id).name
            context={'success':'1','deliery_list':deliery_list,'staff_name':staff_name,}
            return render(request,'operate/deliery_operate.html',context)
        elif request.POST.get("update_deliery_id"):
            deliery_id=request.POST.get("update_deliery_id")
            print(deliery_id)
            name=request.POST.get("name")
            phonenum=request.POST.get("phonenum")
           
            models.Deliery_staff.objects.filter(num=deliery_id).update(num=deliery_id,name=name,phonenum=phonenum)
            deliery_list=models.Deliery_staff.objects.all()
            staff_name=models.Staff.objects.get(num=staff_id).name
            context={'success':'1','deliery_list':deliery_list,'staff_name':staff_name,}
            return render(request,'operate/deliery_operate.html',context)
@staff_login_required     
def gas_in_operate(request,staff_id):
    if request.method=='GET':
        gas_in_list=models.Gas_in.objects.all()
        staff_name=models.Staff.objects.get(num=staff_id).name
        context={'gas_in_list':gas_in_list,'staff_name':staff_name}
        return render(request,'operate/gas_in_operate.html',context)
    elif request.method=='POST':
        if request.POST.get('insert_gas_in'):
            insert_gas_in=request.POST.get('insert_gas_in')
            insert_date=request.POST.get("insert_date")
            insert_category_id1=request.POST.get("insert_category_id")
            print(insert_category_id1)
            insert_supplier_id1=request.POST.get("insert_supplier_id")
            print(insert_supplier_id1)
            insert_amount=request.POST.get("insert_amount")
            insert_amount=int(insert_amount)
            insert_price=request.POST.get("insert_price")
            
            try:
                with transaction.atomic():
                    insert_category_id=models.Gas_category.objects.get(num=insert_category_id1)
                    insert_supplier_id=models.Supplier.objects.get(num=insert_supplier_id1)
                    models.Gas_in.objects.create(num=insert_gas_in,date=insert_date,category_num=insert_category_id,supplier_num=insert_supplier_id,amount=insert_amount,per_price=insert_price)
                    storage=models.Gas_category.objects.get(num=insert_category_id1).storage 
                    result=models.Gas_category.objects.get(num=insert_category_id1)
                    result.storage=storage+insert_amount
                    result.save()
                gas_in_list=models.Gas_in.objects.all()
                staff_name=models.Staff.objects.get(num=staff_id).name
                context={'success':'1','gas_in_list':gas_in_list,'staff_name':staff_name,}
                return render(request,'operate/gas_in_operate.html',context)
            except Exception as e :
                gas_in_list=models.Gas_in.objects.all()
                staff_name=models.Staff.objects.get(num=staff_id).name
                context={'error':True,'gas_in_list':gas_in_list,'staff_name':staff_name}
                print(f"发生错误: {str(e)}")
                return render(request,'operate/gas_in_operate.html',context)
                            
        elif request.POST.get('selectinf'):
            selectinf=request.POST.get('selectinf')
            fangshi=request.POST.get('fangshi')
            print(selectinf)
            print("fangshi:",fangshi)
            if fangshi=="insert_gas_in":
                filter_list=models.Gas_in.objects.filter(num=selectinf)
            elif fangshi=='insert_date':
                filter_list=models.Gas_in.objects.filter(date=selectinf)
            elif fangshi=='insert_category_id':
                filter_list=models.Gas_in.objects.filter(category_num=selectinf)
            elif fangshi=='insert_supplier_id':
                filter_list=models.Gas_in.objects.filter(supplier_num=selectinf)
            staff_name=models.Staff.objects.get(num=staff_id).name
            context={'filter_list':filter_list,'staff_name':staff_name}
            return render(request,"operate/gas_in_operate.html",context)
@customer_login_required     
def customer_operate(request,customer_pho):
     money=models.Customer.objects.get(phonenum=customer_pho).money
     if request.method=='GET':
         gas_list=models.Gas_category.objects.all()
         customer_name=models.Customer.objects.get(phonenum=customer_pho).name
         context={'gas_list':gas_list,'customer_name':customer_name,"money":money}
         return render(request,'view/view_customer.html',context)
     elif request.method=='POST':
         if request.POST.get('selectinf'):
             selectinf=request.POST.get('selectinf')
             fangshi=request.POST.get('fangshi')
             if fangshi=="gas_id":
                 filter_list=models.Gas_category.objects.filter(num=selectinf)
             elif fangshi=='gas_name':
                 filter_list=models.Gas_category.objects.filter(category_name=selectinf) 
             customer_name=models.Customer.objects.get(phonenum=customer_pho).name     
             context={'filter_list':filter_list,'customer_name':customer_name,"money":money}
             return render(request,"view/view_customer.html",context)
         elif request.POST.get('buy_id'):
             buy_id=request.POST.get('buy_id')
             buy_sum=request.POST.get('buy_sum')
             buy_sum=int(buy_sum)

             thetime=datetime.datetime.now()
             time_format='%Y-%m-%d'
             insert_time=thetime.strftime(time_format)
             insert_customer_pho=models.Customer.objects.get(phonenum=customer_pho)
             
             insert_category_num=models.Gas_category.objects.get(num=buy_id)
             insert_amount=buy_sum
             insert_per_price=models.Gas_category.objects.get(num=buy_id).price
             customer_name=models.Customer.objects.get(phonenum=customer_pho).name
             storage_before=models.Gas_category.objects.get(num=buy_id).storage
             money=models.Customer.objects.get(phonenum=customer_pho).money
             if storage_before>=buy_sum and money>=buy_sum*insert_per_price:
                 try:
                     with transaction.atomic():

                        storage_before=models.Gas_category.objects.get(num=buy_id).storage
                        result=models.Gas_category.objects.get(num=buy_id)
                        result.storage=storage_before-buy_sum
                        result.save()

                        money_after=models.Customer.objects.get(phonenum=customer_pho)
                        money_after.money=money-buy_sum*insert_per_price
                        money_after.save()
                        print(money_after.money)

                        if models.Gas_out.objects.filter(num=1).count()<=0:

                            models.Gas_out.objects.create(num=1,date=insert_time,category_num=insert_category_num,customer_pho=insert_customer_pho,amount=insert_amount,per_price=insert_per_price)

                        else:
                            max_value=models.Gas_out.objects.aggregate(max_value=Max('num'))
                            insert_num=max_value['max_value']+1
                            models.Gas_out.objects.create(num=insert_num,date=insert_time,category_num=insert_category_num,customer_pho=insert_customer_pho,amount=insert_amount,per_price=insert_per_price)
                        gas_list=models.Gas_category.objects.all()
                        address=models.Customer.objects.get(phonenum=customer_pho).address
                     
                        context={'success':True,'gas_list':gas_list,'customer_name':customer_name,"money":money_after.money}

                        return render(request,'view/view_customer.html',context)
                 except Exception as e:
                     print(f"发生错误: {str(e)}")
                     gas_list=models.Gas_category.objects.all()
                     context={'error':True,'gas_list':gas_list,'customer_name':customer_name,'money':money}
                     return render(request,'view/view_customer.html',context)
             else:
                 gas_list=models.Gas_category.objects.all()
                 context={'error':True,'gas_list':gas_list,'customer_name':customer_name,'moeny':money}
                 return render(request,'view/view_customer.html',context)
             
@staff_login_required
def deliery_search(request,staff_id):
    deliery_staff=models.Deliery_staff.objects.all()
    x_list1=[]
    y_list1=[]
    z_list1=[]
    is_in_gas_out=[]
    # x_list1是配送员编号，y_list1是配送员配送总数，z_list1是配送员姓名
    deliery_amount = models.Deliery_gas.objects.values('deliery_id').annotate(total_amount=Coalesce(Sum('gas_out_id__amount'), 0))
    
    for i in deliery_amount:
        a=models.Deliery_staff.objects.get(num=i['deliery_id']).num
        is_in_gas_out.append(a)
    for deliery in deliery_staff:
        x_list1.append(deliery.num)
        z_list1.append(deliery.name)
        if deliery.num in is_in_gas_out:
            for i in deliery_amount:
                if deliery.num==i["deliery_id"]:
                    y_list1.append(i["total_amount"])
                    break
        else:
            y_list1.append(0)
    sorted_data1 = sorted(zip(x_list1, y_list1,z_list1), key=lambda x: x[0],reverse=False)
    x_list1 = [x for x, _,_ in sorted_data1]
    y_list1 = [y for _, y,_ in sorted_data1]
    z_list1 = [z for _, _,z in sorted_data1]
    
    deliery=zip(x_list1,z_list1,y_list1)
    name=models.Staff.objects.get(num=staff_id).name
    # 以上是所有配送员配送总量的数据
   
    
    
    if request.method=='GET':
     
        context={"staff_name":name,"x_list1":x_list1,"y_list1":y_list1,"z_list1":z_list1,"deliery":deliery,"deliery_staff":deliery_staff}
        
        return render(request,'operate/deliery_search.html',context)
    elif request.method=='POST':
        ans_month=0
        deliery_id=request.POST.get("deliery_id")#这是deliery的编号#
        year=request.POST.get("year")
        month=request.POST.get("month")
        print(year,month)
        settime=year+"-"+month
        settime = datetime.datetime.strptime(settime, '%Y-%m')
        print(settime)
        deliery_month_ans = models.Deliery_gas.objects.filter(
        deliery_id=deliery_id,
        gas_out_id__date__year=settime.year,
        
    )
        print("deliery_month_ans:",deliery_month_ans)
        if deliery_month_ans.count()<1:
            print("ans_month=0")
        else:
            
            for i in deliery_month_ans:
                print(i.gas_out_id.date.month)
                if i.gas_out_id.date.month==int(month):
                    ans_month+=i.gas_out_id.amount
        print(ans_month)
        monthrange1=calendar.monthrange(int(settime.year),int(settime.month))
        print(monthrange1)
        # 上述为计算指定年份、月份的配送总量
        day_list_spec=[]
        day_list_spec_y=[]
        for i in deliery_month_ans:
            if i.gas_out_id.date.month==int(settime.month):
                if i.gas_out_id.date.day not in day_list_spec:
                    day_list_spec.append(i.gas_out_id.date.day)
                    day_list_spec_y.append(i.gas_out_id.amount)
                else:
                    index=day_list_spec.index(i.gas_out_id.date.day)
                    day_list_spec_y[index]+=i.gas_out_id.amount
                
        for i in range(monthrange1[1]):
            if i+1 not in day_list_spec:
                day_list_spec.append(i+1)
                day_list_spec_y.append(0)
        sorted_data_spec= sorted(zip(day_list_spec,day_list_spec_y), key=lambda x: x[0],reverse=False)
        day_list_spec=[x for x,_ in sorted_data_spec]
        day_list_spec_y=[y for _,y in sorted_data_spec]
        # 上述为计算指点年月每一日的配送量变化趋势
        deliery_name=models.Deliery_staff.objects.get(num=deliery_id).name
        month_list=[]
        month_list_y=[]
        day_list=[]
        day_list_y=[]
        thetime=datetime.datetime.now()
        print(thetime)
        year_now=thetime.year
        month_now=thetime.month
        monthrange=calendar.monthrange(int(year_now),int(month_now))
        print(monthrange)
        deliery_per_month=models.Deliery_gas.objects.filter(deliery_id=deliery_id).filter(gas_out_id__date__year=year_now)
        
        for i in deliery_per_month:
            if i.gas_out_id.date.month==int(month_now):
                if i.gas_out_id.date.day not in day_list:
                    day_list.append(i.gas_out_id.date.day)
                    day_list_y.append(i.gas_out_id.amount)
                else:
                    index=day_list.index(i.gas_out_id.date.day)
                    day_list_y[index]+=i.gas_out_id.amount
                
        for i in range(monthrange[1]):
            if i+1 not in day_list:
                day_list.append(i+1)
                day_list_y.append(0)
        sorted_data_day= sorted(zip(day_list,day_list_y), key=lambda x: x[0],reverse=False)
        day_list=[x for x,_ in sorted_data_day]
        day_list_y=[y for _,y in sorted_data_day]
        deliery_per_year=models.Deliery_gas.objects.filter(deliery_id=deliery_id).filter(gas_out_id__date__year=year_now)
        for i in deliery_per_year:
            if i.gas_out_id.date.month not in month_list:
                month_list.append(i.gas_out_id.date.month)
                month_list_y.append(i.gas_out_id.amount)
            else:
                index=month_list.index(i.gas_out_id.date.month)
                month_list_y[index]+=i.gas_out_id.amount
        for i in range(12):
            if i+1 not in month_list:
                month_list.append(i+1)
                month_list_y.append(0)
        sorted_data_month= sorted(zip(month_list,month_list_y), key=lambda x: x[0],reverse=False)
        month_list=[x for x,_ in sorted_data_month]
        month_list_y=[y for _,y in sorted_data_month]
        print(day_list_spec,day_list_spec_y)
        print(day_list,day_list_y)
        print(month_list,month_list_y)
        # 以上是对当前一年、一月配送数量数据的梳理
        context={"month_list":month_list,"month_list_y":month_list_y,"day_list":day_list,"day_list_y":day_list_y,"day_list_spec":day_list_spec,"day_list_spec_y":day_list_spec_y,"ans_month":ans_month,"deliery_id":deliery_id,"deliery_name":deliery_name,"month":settime.month,"year":settime.year,'deliery_staff':deliery_staff}
        return render(request,"operate/deliery_search.html",context)
@staff_login_required 
def gas_out_operate(request,staff_id):
    gas_out_list=models.Gas_out.objects.all()
    staff_name=models.Staff.objects.get(num=staff_id).name
    if request.method=='GET':
        context={'gas_out_list':gas_out_list,'staff_name':staff_name}
        return render(request,"operate/gas_out_operate.html",context)
    elif request.method=='POST':
        fangshi=request.POST.get("fangshi")
        selectinf=request.POST.get("selectinf")
        if fangshi=="gas_out_num":
            filter_list=models.Gas_out.objects.filter(num=selectinf)
        elif fangshi=='date':
            filter_list=models.Gas_out.objects.filter(date=selectinf)
        elif fangshi=='categroy_id':
            filter_list=models.Gas_out.objects.filter(category_num__num=selectinf)
        elif fangshi=='customer_pho':
            filter_list=models.Gas_out.objects.filter(customer_pho__phonenum=selectinf)
        elif fangshi=='is_deliery':
            if selectinf=='是':
                filter_list=models.Gas_out.objects.filter(is_deliery=1)
            elif selectinf=='否':
                filter_list=models.Gas_out.objects.filter(is_deliery=0)
        context={'filter_list':filter_list,"staff_name":staff_name,}
        return render(request,"operate/gas_out_operate.html",context)
@staff_login_required
def view_deliery(request,deliery_id):
    total_amount=0
    deliery_amount = models.Deliery_gas.objects.values('deliery_id').annotate(total_amount=Coalesce(Sum('gas_out_id__amount'), 0))
    for i in deliery_amount:
        
        if int(i['deliery_id'])==deliery_id:
            
            total_amount=i['total_amount']
            
    print(deliery_id,total_amount)
    deliery_name=models.Deliery_staff.objects.get(num=deliery_id).name
    month_list=[]
    month_list_y=[]
    day_list=[]
    day_list_y=[]
    thetime=datetime.datetime.now()
    print(thetime)
    year_now=thetime.year
    month_now=thetime.month
    monthrange=calendar.monthrange(int(year_now),int(month_now))
    print(monthrange)
    deliery_per_month=models.Deliery_gas.objects.filter(deliery_id=deliery_id).filter(gas_out_id__date__year=year_now)
        
    for i in deliery_per_month:
        if i.gas_out_id.date.month==int(month_now):
            if i.gas_out_id.date.day not in day_list:
                day_list.append(i.gas_out_id.date.day)
                day_list_y.append(i.gas_out_id.amount)
            else:
                index=day_list.index(i.gas_out_id.date.day)
                day_list_y[index]+=i.gas_out_id.amount
                
    for i in range(monthrange[1]):
        if i+1 not in day_list:
            day_list.append(i+1)
            day_list_y.append(0)
    sorted_data_day= sorted(zip(day_list,day_list_y), key=lambda x: x[0],reverse=False)
    day_list=[x for x,_ in sorted_data_day]
    day_list_y=[y for _,y in sorted_data_day]
    deliery_per_year=models.Deliery_gas.objects.filter(deliery_id=deliery_id).filter(gas_out_id__date__year=year_now)
    for i in deliery_per_year:
        if i.gas_out_id.date.month not in month_list:
            month_list.append(i.gas_out_id.date.month)
            month_list_y.append(i.gas_out_id.amount)
        else:
            index=month_list.index(i.gas_out_id.date.month)
            month_list_y[index]+=i.gas_out_id.amount
    for i in range(12):
        if i+1 not in month_list:
            month_list.append(i+1)
            month_list_y.append(0)
    sorted_data_month= sorted(zip(month_list,month_list_y), key=lambda x: x[0],reverse=False)
    month_list=[x for x,_ in sorted_data_month]
    month_list_y=[y for _,y in sorted_data_month]
    context={'day_list':day_list,'day_list_y':day_list_y,'month_list':month_list,'month_list_y':month_list_y,'deliery_name':deliery_name,'total_amount':total_amount,'deliery_id':deliery_id}
    return render(request,"view/view_deliery.html",context)
def home_customer(request,customer_pho):
    gas_out=models.Gas_out.objects.filter(customer_pho__phonenum=customer_pho)
    gas_out_num=[]
    gas_out_date=[]
    gas_out_category_num=[]
    gas_out_category_name=[]
    gas_out_amount=[]
    gas_out_per_price=[]
    deliery_id_list=[]
    deliery_name_list=[]
    deliery_phonenum_list=[]
    status=[]
    status_ini=[]
    for i in gas_out:
        gas_out_num.append(i.num)
        gas_out_date.append(i.date)
        gas_out_category_num.append(i.category_num.num)
        gas_out_category_name.append(i.category_num.category_name)
        gas_out_amount.append(i.amount)
        gas_out_per_price.append(i.per_price)
        try:
            deliery_id=models.Deliery_gas.objects.get(gas_out_id__num=i.num).deliery_id.num
            deliery_name=models.Deliery_gas.objects.get(gas_out_id__num=i.num).deliery_id.name
            deliery_phonenum=models.Deliery_gas.objects.get(gas_out_id__num=i.num).deliery_id.phonenum
            deliery_id_list.append(deliery_id)
            deliery_name_list.append(deliery_name)
            deliery_phonenum_list.append(deliery_phonenum)
        except Exception as e:
            deliery_id_list.append('未分配配送员')
            deliery_name_list.append('未分配配送员')
            deliery_phonenum_list.append('未分配配送员')
        
        if i.is_deliery==0:
            status_one="未配送"
            status_ini.append(0)
        elif i.is_deliery==1:
            status_one="配送中"
            status_ini.append(0)
        elif i.is_deliery==2:
            status_one="已收货"
            status_ini.append(1)
        
        status.append(status_one)
    gas_out_view=zip(gas_out_num,gas_out_date,gas_out_category_num,gas_out_category_name,gas_out_amount,gas_out_per_price,deliery_id_list,deliery_name_list,deliery_phonenum_list,status,status_ini)
    if request.method=='GET':
        context={'gas_out_view':gas_out_view}
        return render(request,"view/home_customer.html",context)
    elif request.method=='POST':
        if request.POST.get('confirm_id'):
            gas_out_view_num=int(request.POST.get('confirm_id'))
            result=models.Gas_out.objects.get(num=gas_out_view_num)
            if result.is_deliery==1:

                result.is_deliery=2
                result.save()
                context={'gas_out_view':gas_out_view,'customer_pho':customer_pho}
                return render(request,"view/home_customer.html",context)
            else:
                
                context={'error':True,'gas_out_view':gas_out_view,'customer_pho':customer_pho}
                return render(request,"view/home_customer.html",context)


def gas_operate(request,staff_id):
    gas_list=models.Gas_category.objects.all()
    staff_name=models.Staff.objects.get(num=staff_id).name
    if request.method=='GET':
        
        context={'gas_list':gas_list,'staff_name':staff_name}
        return render(request,"operate/gas_operate.html",context)
    elif request.method=='POST':
        if request.POST.get("insert_gas_id"):
            gas_id=request.POST.get("insert_gas_id")
            category_name=request.POST.get("category_name")
            description=request.POST.get("description")
            try:
                models.Gas_category.objects.create(num=gas_id,category_name=category_name,description=description,storage=0,price=0)
                gas_list=models.Gas_category.objects.all()
                staff_name=models.Staff.objects.get(num=staff_id).name
                context={'success':'1','gas_list':gas_list,'staff_name':staff_name,}
                return render(request,'operate/gas_operate.html',context)
            except:
                context={'error':True,'gas_list':gas_list,'staff_name':staff_name,}
                return render(request,'operate/gas_operate.html',context)
            
        elif request.POST.get("selectinf"):
            selectinf=request.POST.get("selectinf")
            filter_inf1=models.Gas_category.objects.filter(num=selectinf)
            filter_result=models.Gas_category.objects.filter(category_name=selectinf).union(filter_inf1)           
            staff_name=models.Deliery_staff.objects.get(num=staff_id).name
            context={'filter_result':filter_result,'staff_name':staff_name}
            return render(request,'operate/gas_operate.html',context)
        elif request.POST.get("delete_gas_id"):
            delete_gas_id=request.POST.get('delete_gas_id')
            print(delete_gas_id)
            data=models.Gas_category.objects.filter(num=delete_gas_id).first()
            data.delete()
            gas_list=models.Gas_category.objects.all()
            staff_name=models.Staff.objects.get(num=staff_id).name
            context={'success':'1','gas_list':gas_list,'staff_name':staff_name,}
            return render(request,'operate/gas_operate.html',context)
        elif request.POST.get("update_gas_id"):
            gas_id=request.POST.get("update_gas_id")
            print(gas_id)
            category_name=request.POST.get("update_category_name")
            description=request.POST.get("update_description")
            storage=int(request.POST.get('storage'))
            price=int(request.POST.get('per_price'))
            models.Gas_category.objects.filter(num=gas_id).update(num=gas_id,category_name=category_name,storage=storage,price=price,description=description)
            gas_list=models.Gas_category.objects.all()
            staff_name=models.Staff.objects.get(num=staff_id).name
            context={'success':'1','gas_list':gas_list,'staff_name':staff_name,}
            return render(request,'operate/gas_operate.html',context)


         
      
         
     



        




        

    

             

        

       
            

        
            
