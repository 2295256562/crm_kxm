from django.urls import path,re_path
from crm.views import consultant,teacher

urlpatterns = [
   # path('customer_list/', views.customer_list, name='custmoer'), # 公户
   path('customer_list/', consultant.CustomerList.as_view(), name='custmoer'), # 公户
   # path('my_customer/', views.customer_list, name='my_customer'), # 公户
   path('my_customer/', consultant.CustomerList.as_view(), name='my_customer'), # 公户
   path('customer/add/', consultant.custmoer, name='add_custmoer'),  # 增加
   path('customer/edit/<edit_id>', consultant.custmoer, name='edit_custmoer'),  # 编辑


   # 展示跟进记录
   re_path(r'consult_record_list/(?P<customer_id>\d+)', consultant.ConsultRecord.as_view(), name='consult_record'),
   # 新增跟进记录
   path('add_consult/', consultant.consult, name='add_record'),
   # 编辑跟进记录
   path('edit_consult/<edit_id>', consultant.consult, name='edit_record'),
   # 展示报名记录
   re_path('enrollment_list/(?P<customer_id>\d+)', consultant.EnrollmentList.as_view(), name='enrollment'),
   # 添加报名记录
   re_path('enrollment/add/(?P<customer_id>\d+)', consultant.enrollment, name='add_enrollment'),
   # 修改报名记录
   re_path('enrollment/edit/(?P<customer_id>\d+)', consultant.enrollmentEdit, name='edit_enrollment'),


   # 展示班级
   re_path(r'class_list/', teacher.ClassList.as_view(), name='class_list'),
   # 新增
   re_path(r'class/add/', teacher.classes, name='add_class'),
   # 编辑
   re_path(r'class/edit/(\d+)', teacher.classes, name='edit_class'),


   # 展示某个课程记录
   re_path(r'course_list/(?P<class_id>\d+)', teacher.course_list.as_view(), name='course_list'),
   # 新增
   re_path(r'course/add/', teacher.course, name='add_course'),
   # 编辑
   re_path(r'course/edit(\d+)', teacher.course, name='edit_course')
]
