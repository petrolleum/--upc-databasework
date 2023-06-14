from django import forms
class Login_staff(forms.Form):
    staff_id=forms.CharField(label="员工编号")
    password=forms.CharField(label="密码")
class Login_customer(forms.Form):
    customer_id=forms.CharField(label='客户编号')
    password=forms.CharField(label="密码")
class Login_supplier(forms.Form):
    supplier_id=forms.CharField(label='供应商编号')
    password=forms.CharField(label="密码")
class Register(forms.Form):
    name=forms.CharField(label='客户姓名')
    phonenum=forms.CharField(label='电话号码')
    address=forms.CharField(label='送货地址')
    password=forms.CharField(label='密码')
class Insert_supplier(forms.Form):
    supplier_id=forms.CharField(label='请输入编号')
    name=forms.CharField(label='请输入姓名')
    phonenum=forms.CharField(label='请输入电话号码')
    
class Select_supplier(forms.Form):
    selectinf=forms.CharField()
class Delete(forms.Form):
    supplier_id=forms.CharField(max_length=20,label='确认删除'),
class Update(forms.Form): 
    supplier_id=forms.CharField(label='请输入编号')
    name=forms.CharField(label='请输入姓名')
    phonenum=forms.CharField(label='请输入电话号码')
    