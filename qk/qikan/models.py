from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.

class EmailTemplate(models.Model):
    """邮件模板模型"""
    title = models.CharField(max_length=255, verbose_name='模板标题')
    content = models.TextField(verbose_name='模板内容')  # 存储HTML格式内容
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'email_template'
        verbose_name = '邮件模板'
        verbose_name_plural = '邮件模板'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Mail(models.Model):
    type = models.CharField(max_length=255)
    sender = models.CharField(max_length=255)
    recipient = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    date = models.CharField(max_length=255)
    body = models.TextField()
    attachments = models.JSONField(null=True)

    class Meta:
        db_table = 'mail'
        managed = False  # 不让 Django 管理这个表
        app_label = 'qikan'  # 指定 app
        db_table_comment = "外部创建的邮件表"  # 添加表注释，方便识别

    def __str__(self):
        return self.subject

class JournalPeriodBase(models.Model):
    filename = models.CharField(max_length=255, verbose_name='文件名')
    editor_in_charge = models.CharField(max_length=50, verbose_name='责编', blank=True)
    page_fee = models.CharField(max_length=50, verbose_name='版面费', default='待更新')
    
    # 校对状态
    proof_status = models.CharField(max_length=50, verbose_name='校对情况', default='待更新')
    
    # 校对编辑
    first_second_proof_editor = models.CharField(max_length=50, verbose_name='一、二校编辑', blank=True)
    third_proof_editor = models.CharField(max_length=50, verbose_name='三校编辑', blank=True)
    final_proof_editor = models.CharField(max_length=50, verbose_name='终校编辑', blank=True)
    
    # 时间记录
    editor_time = models.CharField(max_length=50, verbose_name='责编时间', blank=True)
    proof_time = models.CharField(max_length=50, verbose_name='校对时间', blank=True)
    remarks = models.CharField(max_length=50, verbose_name='备注', blank=True)
    
    # 版次信息
    edition = models.CharField(max_length=50, verbose_name='版次', blank=True, default='')

    class Meta:
        abstract = True
        ordering = ['id']

class JournalPeriodOne(JournalPeriodBase):
    class Meta:
        verbose_name = '第一期'
        verbose_name_plural = verbose_name

class JournalPeriodTwo(JournalPeriodBase):
    class Meta:
        verbose_name = '第二期'
        verbose_name_plural = verbose_name

class JournalPeriodThree(JournalPeriodBase):
    class Meta:
        verbose_name = '第三期'
        verbose_name_plural = verbose_name

class JournalPeriodFour(JournalPeriodBase):
    class Meta:
        verbose_name = '第四期'
        verbose_name_plural = verbose_name

class JournalPeriodFive(JournalPeriodBase):
    class Meta:
        verbose_name = '第五期'
        verbose_name_plural = verbose_name

class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    article_id = models.CharField(max_length=100)
    article = models.CharField(max_length=200, blank=True)
    amount = models.CharField(max_length=50, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    type = models.CharField(max_length=50, blank=True)
    tag = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=200, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    contact = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = '发票'
        verbose_name_plural = verbose_name
        ordering = ['-id']

class ArticleSchedule(models.Model):
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=100, verbose_name='文件')
    schedule = models.CharField(max_length=20, verbose_name='排期', blank=True)
    confirmed = models.CharField(max_length=20, verbose_name='是否确认', default='待更新')
    notes = models.TextField(verbose_name='备注', blank=True)

    class Meta:
        verbose_name = '文章排期'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.filename

class PeriodMapping(models.Model):
    backend_period = models.IntegerField(unique=True, verbose_name='后端期数')  # 1-5
    display_period = models.IntegerField(verbose_name='显示期数')  # 1-12
    
    class Meta:
        verbose_name = '期数映射'
        verbose_name_plural = verbose_name
        ordering = ['backend_period']

    def __str__(self):
        return f'后端期数{self.backend_period} -> 显示期数{self.display_period}'

class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    postcode = models.CharField(max_length=10, verbose_name='邮编', blank=True)
    name = models.CharField(max_length=20, verbose_name='姓名')
    phone = models.CharField(max_length=15, verbose_name='手机', blank=True)
    address = models.CharField(max_length=200, verbose_name='地址', blank=True)
    email = models.CharField(max_length=50, verbose_name='邮箱', blank=True)
    notes = models.CharField(max_length=50, verbose_name='备注', blank=True)
    label = models.CharField(max_length=20, verbose_name='标签')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '作者通讯录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.label}'

class Reviewer(models.Model):
    """责编信息模型"""
    id = models.AutoField(primary_key=True)
    year = models.IntegerField(verbose_name='年份', blank=True, null=True)
    period = models.IntegerField(verbose_name='期次', blank=True, null=True)
    name = models.CharField(max_length=100, verbose_name='姓名', blank=True, null=True)
    workplace = models.CharField(max_length=200, verbose_name='工作单位', blank=True, null=True)
    id_card = models.CharField(max_length=18, verbose_name='身份证号', blank=True, null=True)
    bank_account = models.CharField(max_length=50, verbose_name='银行卡号', blank=True, null=True)
    bank_name = models.CharField(max_length=100, verbose_name='开户行', blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name='手机', blank=True, null=True)
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='应发', default=0, blank=True, null=True  )
    tax = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='税金', default=0, blank=True, null=True)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='实发', default=0, blank=True, null=True)
    notes = models.TextField(verbose_name='备注', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'qikan_reviewer'
        verbose_name = '责编信息'
        verbose_name_plural = verbose_name
        ordering = ['-year', '-period', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.year}年第{self.period}期)"

class Todo(models.Model):
    """待办事项模型"""
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
    ]
    
    STATUS_CHOICES = [
        ('in_progress', '进行中'),
        ('completed', '已完成'),
    ]
    
    USER_CHOICES = [
        ('孙航', '孙航'),
        ('李彦燕', '李彦燕'),
        ('陈玉忠', '陈玉忠'),
        ('孔源博', '孔源博'),
        ('新用户1', '新用户1'),
        ('新用户2', '新用户2'),
    ]
    
    id = models.AutoField(primary_key=True)
    content = models.TextField(verbose_name='任务内容')
    assignee = models.CharField(max_length=20, choices=USER_CHOICES, verbose_name='添加人')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress', verbose_name='状态')
    due_date = models.DateField(null=True, blank=True, verbose_name='截止日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'qikan_todo'
        verbose_name = '待办事项'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.content[:50]}... - {self.assignee}"


class RecipientGroup(models.Model):
    """联系人分组模型"""
    name = models.CharField(max_length=100, primary_key=True, verbose_name="分组名称")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'recipient_group'
        verbose_name = '联系人分组'
        verbose_name_plural = verbose_name
        ordering = ['name']

    def __str__(self):
        return self.name

class Recipient(models.Model):
    """联系人模型"""
    name = models.CharField(max_length=100, verbose_name="姓名")
    email = models.EmailField(max_length=255, unique=False, db_index=True, verbose_name="邮箱")
    # 多对多关联分组。通过中间表管理成员关系。
    # 注意：后续迁移会从旧的外键列迁移到多对多关系。
    groups = models.ManyToManyField(
        RecipientGroup,
        through='RecipientGroupMembership',
        related_name='members',
        verbose_name='所属分组',
        blank=True,
    )
    remark = models.TextField(blank=True, null=True, verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'recipient'
        verbose_name = '联系人'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} <{self.email}>"


class RecipientGroupMembership(models.Model):
    """联系人-分组 联结表（多对多中间表）"""
    recipient = models.ForeignKey('Recipient', on_delete=models.CASCADE, verbose_name='联系人')
    group = models.ForeignKey(RecipientGroup, to_field='name', on_delete=models.CASCADE, verbose_name='分组')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'recipient_group_membership'
        verbose_name = '联系人-分组关联'
        verbose_name_plural = verbose_name
        unique_together = (('recipient', 'group'),)
        indexes = [
            models.Index(fields=['recipient'], name='idx_rg_recipient'),
            models.Index(fields=['group'], name='idx_rg_group'),
        ]


class JournalProgressSummary(models.Model):
    """期刊进度管理汇总表，用于存储清空前的历史数据"""
    # 来源信息
    source_period = models.IntegerField(verbose_name='来源期数', help_text='1-5，表示来自第几期')
    archived_at = models.DateTimeField(auto_now_add=True, verbose_name='归档时间')
    
    # 期刊信息字段（与 JournalPeriodBase 保持一致）
    filename = models.CharField(max_length=255, verbose_name='文件名')
    editor_in_charge = models.CharField(max_length=50, verbose_name='责编', blank=True)
    page_fee = models.CharField(max_length=50, verbose_name='版面费', default='待更新')
    
    # 校对状态
    proof_status = models.CharField(max_length=50, verbose_name='校对情况', default='待更新')
    
    # 校对编辑
    first_second_proof_editor = models.CharField(max_length=50, verbose_name='一、二校编辑', blank=True)
    third_proof_editor = models.CharField(max_length=50, verbose_name='三校编辑', blank=True)
    final_proof_editor = models.CharField(max_length=50, verbose_name='终校编辑', blank=True)
    
    # 时间记录
    editor_time = models.CharField(max_length=50, verbose_name='责编时间', blank=True)
    proof_time = models.CharField(max_length=50, verbose_name='校对时间', blank=True)
    remarks = models.CharField(max_length=50, verbose_name='备注', blank=True)
    
    # 版次信息
    edition = models.CharField(max_length=50, verbose_name='版次', blank=True, default='')

    class Meta:
        db_table = 'journal_progress_summary'
        verbose_name = '期刊进度汇总'
        verbose_name_plural = verbose_name
        ordering = ['-archived_at', 'source_period']

    def __str__(self):
        return f"第{self.source_period}期 - {self.filename} ({self.archived_at.strftime('%Y-%m-%d %H:%M')})"


class UpdateLog(models.Model):
    """更新日志，仅后端维护，前端读取最新一条显示"""
    id = models.AutoField(primary_key=True)
    content = models.TextField(verbose_name='更新内容')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'update_log'
        verbose_name = '更新日志'
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']

    def __str__(self):
        return f"更新于 {self.updated_at}"
