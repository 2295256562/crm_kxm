from django.views import View
import time

from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import auth
from django.views.generic import ListView
from crm import models
from crm.forms import RegForm, CustomerForm, ConsultRecordForm, EnrollmentForm, classForm,CourseForm
from crm.models import Customer, ConsultRecord
from django.views import View
from django.db.models import Q
from utils.pagination import Pagination
from django.utils.safestring import mark_safe
from django.http import QueryDict
import copy
from django.db import transaction  # 事务
from django.conf import settings


# 班级展示
class ClassList(View):
    def get(self, request):
        q = self.get_seache_contion(['course', 'semester'])
        all_class = models.ClassList.objects.filter(q)

        # 获取路径
        query_params = self.get_query_params()

        # 分页应用
        page = Pagination(request, len(all_class), request.GET.copy())
        return render(request, 'crm/teacher/class_list.html',
                      {"all_class": all_class[page.start:page.end], 'pagination': page.show_li,
                       'query_params': query_params})

    def get_seache_contion(self, query_list):
        """模糊查询"""
        query = self.request.GET.get('query', '')

        q = Q()
        q.connector = 'OR'
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))  # 进行拼接
        return q

    def get_query_params(self):
        """ 获取添加按钮"""
        url = self.request.get_full_path()

        qd = QueryDict()
        qd._mutable = True
        qd['next'] = url
        query_params = qd.urlencode()

        return query_params


# 新增编辑
def classes(request, edit_id=None):
    obj = models.ClassList.objects.filter(id=edit_id).first()
    form_obj = classForm(instance=obj)
    title = '编辑班级' if obj else '新增班级'
    if request.method == 'POST':
        form_obj = classForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            next = request.GET.get('next')
            if next:
                return redirect(next)
            return redirect(reverse('class_list'))
    return render(request, 'crm/form.html', {'title': title, 'form_obj': form_obj})

# 课程展示
class course_list(View):

    def get(self, request, class_id):
        q = self.get_seache_contion([])
        all_course = models.CourseRecord.objects.filter(q, re_class_id=class_id)

        # 获取路径
        query_params = self.get_query_params()

        # 分页应用
        page = Pagination(request, len(all_course), request.GET.copy())
        return render(request, 'crm/teacher/course_list.html', {"all_course": all_course[page.start:page.end], 'pagination': page.show_li,'query_params': query_params})

    def get_seache_contion(self, query_list):
        """模糊查询"""
        query = self.request.GET.get('query', '')

        q = Q()
        q.connector = 'OR'
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))  # 进行拼接
        return q

    def get_query_params(self):
        """ 获取添加按钮"""
        url = self.request.get_full_path()

        qd = QueryDict()
        qd._mutable = True
        qd['next'] = url
        query_params = qd.urlencode()

        return query_params


# 新增编辑
def course(request, edit_id=None):
    obj = models.CourseRecord.objects.filter(id=edit_id).first()
    form_obj = CourseForm(instance=obj)
    title = '编辑课程' if obj else '新增课程'
    if request.method == 'POST':
        form_obj = classForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            next = request.GET.get('next')
            if next:
                return redirect(next)
            return redirect(reverse('class_list'))
    return render(request, 'crm/form.html', {'title': title, 'form_obj': form_obj})



