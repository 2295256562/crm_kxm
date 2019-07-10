import time

from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import auth
from django.views.generic import ListView
from crm import models
from crm.forms import RegForm, CustomerForm,ConsultRecordForm,EnrollmentForm
from crm.models import Customer, ConsultRecord
from django.views import View
from django.db.models import Q
from utils.pagination import Pagination
from django.utils.safestring import mark_safe
from django.http import QueryDict
import copy
from django.db import transaction     # 事务
from django.conf import settings


# 登陆
def login(request):
    if request.method == 'POST':
        user = request.POST.get('user')
        password = request.POST.get('password')
        obj = auth.authenticate(request, username=user, password=password)
        if obj:
            auth.login(request, obj)
            return redirect(reverse('my_customer'))
    err_msg = "用户名或密码错误"

    return render(request, 'login.html', {"err_msg": err_msg})

# 注册
def reg(request):
    form_obj = RegForm()

    if request.method == 'POST':
        form_obj = RegForm(request.POST)
        if form_obj.is_valid():
            obj = form_obj.save()
            obj.set_password(obj.password)
            obj.save()

            return redirect('/login/')
    return render(request, 'reg.html', {'form_obj': form_obj})


# 展示客户列表
def customer_list(request):
    print(request.POST)
    if request.path_info == reverse('custmoer'):
        all_customer = models.Customer.objects.filter(consultant__isnull=True)  # 查询consultant等于空的
    else:
        all_customer = models.Customer.objects.filter(consultant=request.user)  # 查询consultant等于当前登录的用户
    page = Pagination(request, all_customer.count())
    return render(request, 'crm/consultant/customer_list.html', {'all_customer': all_customer[page.start:page.end], 'pagination' : page.show_li})


# 展示客户列表
class CustomerList(View):

    def get(self, request):

        # q = Q()
        # q.connector = 'OR'
        # q.children.append(Q(('qq__contains', query)))
        # q.children.append(Q(('name__contains', query)))
        q = self.get_seache_contion(['name', 'qq', 'last_consult_date'])    # 查询的条件

        if request.path_info == reverse('custmoer'):
            all_customer = models.Customer.objects.filter(q, consultant__isnull=True)  # 查询consultant等于空的
        else:
            all_customer = models.Customer.objects.filter(q, consultant=request.user)  # 查询consultant等于当前登录的用户
        query_params = copy.deepcopy(request.GET)  # 深拷贝
        print(query_params)
        page = Pagination(request, all_customer.count(), query_params, 2)

        add_btn,query_params = self.get_add_btn()
        return render(request, 'crm/consultant/customer_list.html', {'all_customer': all_customer[page.start:page.end], 'pagination' : page.show_li, 'add_btn': add_btn, 'query_params': query_params})

    def post(self, request):
        # 处理post提交action的动作
        print(request.POST)
        action = request.POST.get('action')

        if not hasattr(self, action):
            return HttpResponse('非法操作')

        ret = getattr(self, action)()

        return self.get(request)

    def multi_apply(self):
        """公户变私户"""
        # 方法1
        ids = self.request.POST.getlist('id')
        # models.Customer.objects.filter(id__in=ids).update(consultant=self.request.user)  # 用传过来的id查询，然后修改销售为当前用户
        apply_num = len(ids)

        # 用户总数不能超过设置值 CUSTOMER_MAX_NUM
        if self.request.user.customers.count() + apply_num > settings.CUSTOMER_MAX_NUM:
            return HttpResponse('做人不要太贪心，给别人点机会')

        with transaction.atomic():
            # 事务
            # select_for_update 加🔐锁
            obj_list = models.Customer.objects.filter(id__in=ids, consultant__isnull=True).select_for_update()
            if apply_num == len(obj_list):
                obj_list.update(consultant=self.request.user)
            else:
                return HttpResponse('你的手速太慢')
        # 方法2
        # self.request.user.customers.add(*models.Customer.objects.filter(id__in=ids))

    def multi_plu(self):
        """私户变公户  函数名对应value"""
        ids = self.request.POST.getlist('id')
        models.Customer.objects.filter(id__in=ids).update(consultant=None)  # 用传过来的id查询，然后修改销售为当前用户

        # *为打散的意思;只有当外键null=True才有revmore和clear方法
        # self.request.user.customers.revmore(*models.Customer.objects.filter(id__in=ids))

    def get_seache_contion(self, query_list):
        """模糊查询"""
        query = self.request.GET.get('query', '')

        q = Q()
        q.connector = 'OR'
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))     # 进行拼接
        return q

    def get_add_btn(self):
        """ 获取添加按钮"""
        url = self.request.get_full_path()

        qd = QueryDict()
        qd._mutable = True
        qd['next'] = url
        query_params = qd.urlencode()
        add_btn = ' <a href="{}?{}" class="btn btn-primary btn-group-sm">添加</a>'.format(reverse('add_custmoer'), query_params)
        return mark_safe(add_btn), query_params


# 添加客户
def add_custmoer(request):
    form_obj = CustomerForm()  # 实例化
    if request.method == 'POST':
        # 实例化一个待提交的form对象
        form_obj = CustomerForm(request.POST)
        # 对提交数据进行校验
        if form_obj.is_valid():
            # 创建对象
            form_obj.save()
            return redirect(reverse('custmoer'))
    return render(request, 'crm/consultant/add_custmoer.html', {'form_obj': form_obj})


# 编辑客户
def edit_custmoer(request, edit_id):
    obj = models.Customer.objects.filter(id=edit_id).first()  # 根据id查出所需要编辑的客户
    form_obj = CustomerForm(instance=obj)  # 实例obj  用接收到的obj去CustomerForm里查询

    if request.method == 'POST':
        # 将提交的数据和要修改的实例交给form对象
        form_obj = CustomerForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()  # 对要修改的实例进行修改
            return redirect(reverse('custmoer'))
    return render(request, 'crm/consultant/edit_custmoer.html', {"form_obj": form_obj})


# 新增和编辑客户
def custmoer(request, edit_id=None):
    obj = models.Customer.objects.filter(id=edit_id).first()
    form_obj = CustomerForm(instance=obj)  # 实例obj  用接收到的obj去CustomerForm里查询

    if request.method == 'POST':
        # 将提交的数据和要修改的实例交给form对象
        form_obj = CustomerForm(request.POST, instance=obj)
        if form_obj.is_valid():
            # 创建一个新的数据
            form_obj.save()  # 对要修改的实例进行修改

            # 获取next
            next = request.GET.get('next')

            if next:
                return redirect(next)

            return redirect(reverse('custmoer'))
    return render(request, 'crm/consultant/custmoer.html', {"form_obj": form_obj, "edit_id": edit_id})

# 展示跟进记录
class ConsultRecord(View):

    def get(self, request, customer_id):

        if customer_id == '0':
            all_consult_record = models.ConsultRecord.objects.filter(delete_status=False, consultant=request.user)
        else:
            all_consult_record = models.ConsultRecord.objects.filter(customer_id=customer_id, delete_status=False)
        return render(request, 'crm/consultant/consult_record_list.html', {"all_consult_record": all_consult_record})

# 添加跟进记录
def add_consult(request):
    obj = models.ConsultRecord(consultant=request.user)  # 在内存当中

    form_obj = ConsultRecordForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultRecordForm(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_record'))       # 跳转到列表页
    return render(request, 'crm/consultant/add_consult.html', {"form_obj": form_obj})

# 编辑跟进记录
def edid_consult(request, edit_id):
    obj = models.ConsultRecord.objects.filter(id=edit_id).first()
    form_obj = ConsultRecordForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultRecordForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_record'))  # 跳转到列表页
    return render(request, 'crm/consultant/edit_consult.html', {"form_obj": form_obj})

# 新增和编辑跟进记录
def consult(request, edit_id=None):
    print(edit_id)
    obj = models.ConsultRecord.objects.filter(id=edit_id).first() or models.ConsultRecord(consultant=request.user)
    form_obj = ConsultRecordForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultRecordForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_record', args=(0, )))  # 跳转到列表页
    return render(request, 'crm/consultant/edit_consult.html', {"form_obj": form_obj})

# 展示报名记录
class EnrollmentList(View):

    def get(self, request, customer_id):

        if customer_id == '0':
            all_record = models.Enrollment.objects.filter(delete_status=False, customer__consultant=request.user)
        else:
            all_record = models.Enrollment.objects.filter(customer_id=customer_id, delete_status=False)
        return render(request, 'crm/consultant/enrollment_list.html', {"all_record": all_record})

# 添加报名记录
def enrollment(request, customer_id):

    obj = models.Enrollment(customer_id=customer_id)
    form_obj = EnrollmentForm(instance=obj)
    if request.method == 'POST':
        form_obj = EnrollmentForm(request.POST, instance=obj)
        if form_obj.is_valid():
            enrollment_obj = form_obj.save()

            # 修改客户状态变成已报名
            enrollment_obj.customer.status = 'signed'
            # 保存修改之后的状态
            enrollment_obj.customer.save()

            next = request.GET.get('next')
            if next:
                return redirect(next)
            else:
                return redirect(reverse('my_customer'))
    return render(request, 'crm/consultant/enrollment.html', {"form_obj": form_obj})


def enrollmentEdit(request, customer_id):
    obj = models.Enrollment.objects.filter(id=customer_id).first()
    form_obj = EnrollmentForm(instance=obj)
    if request.method == 'POST':
        form_obj = EnrollmentForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('enrollment'))
    return render(request, 'crm/consultant/edit_enrollment.html', {"form_obj": form_obj})
