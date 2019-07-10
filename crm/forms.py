from django import forms
from django.core.exceptions import ValidationError

from crm import models

class baseForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

# 注册
class RegForm(baseForm):
    password = forms.CharField(
        label='密码',
        widget=forms.widgets.PasswordInput(),
        min_length=6,  # 最小长度6
        error_messages={'min_length': '最小长度为6'}
    )

    re_password = forms.CharField(
        label='确认密码',
        widget=forms.widgets.PasswordInput(),
    )

    class Meta:
        model = models.UserProfile
        fields = ['username', 'password', 're_password', 'name', 'department']  # 指定字段

        # 插件
        widgets = {
            'username': forms.widgets.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.widgets.PasswordInput,
        }

        # 显示中文名， 等同models给字段加verbose_name
        labels = {
            'username': '用户名',
            'password': '密码',
            'name': '姓名',
            'department': '部门'
        }

        # 字段的错误信息
        error_messages = {
            'password': {
                'required': '密码不能为空',       # 必填
            }
        }

    def clean(self):
        pwd = self.cleaned_data.get('password')
        re_pwd = self.cleaned_data.get('re_password')
        if pwd == re_pwd:
            return self.cleaned_data
        self.add_error('re_password', '两次密码不一致')
        raise ValidationError('两次密码不一致')

# 客户form
class CustomerForm(baseForm):
    class Meta:
        model = models.Customer
        fields = '__all__'
        widgets = {
            'course': forms.widgets.SelectMultiple
        }

# 跟进记录form
class ConsultRecordForm(baseForm):

    class Meta:
        model = models.ConsultRecord
        exclude = ['delete_status']

        labels = {
            'note': '跟进内容',
        }

        # widgets = {
        #     'customer': forms.Widgets.select(chocies=((1, 'xxx'),))
        # }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 限制客户是当前销售的私户
        self.fields['customer'].widget.choices = [(i.id, i) for i in self.instance.consultant.customers.all()]     # 拿到当前销售的所有客户
        # 限制跟进人是当前的用户（销售）
        self.fields['consultant'].widget.choices = [(self.instance.consultant.id, self.instance.consultant),]

# 报名记录form
class EnrollmentForm(baseForm):

    class Meta:
        model = models.Enrollment
        exclude = ['delete_status', 'contract_approved']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 限制当前的客户只能是传的id对应的客户
        self.fields['customer'].widget.choices = [(self.instance.customer_id, self.instance.customer),]
        # 限制当前可报名的班级是当前意向的班级
        self.fields['enrolment_class'].widget.choices = [ (i.id, i) for i in self.instance.customer.class_list.all()]


# 班级列表from
class classForm(baseForm):

    class Meta:
        model = models.ClassList
        fields = '__all__'

# 课程记录表
class CourseForm(baseForm):

    class Meta:
        model = models.CourseRecord
        fields = '__all__'