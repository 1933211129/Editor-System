from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'contacts', views.ContactViewSet)
router.register(r'reviewers', views.ReviewerViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/email/send-bulk/', views.send_bulk_email, name='send_bulk_email'), # 发送邮件
    # 临时附件上传相关
    path('api/email/upload/', views.upload_email_attachments, name='upload_email_attachments'), # 上传邮件附件
    path('api/email/uploads/', views.list_email_uploads, name='list_email_uploads'), # 列出邮件上传
    path('api/email/uploads/clear/', views.clear_email_uploads, name='clear_email_uploads'), # 清除邮件上传
    path('api/email/history/', views.get_email_history, name='email_history'), # 获取邮件历史
    path('api/auth/register/', views.user_register, name='user_register'), # 注册
    path('api/auth/login/', views.user_login, name='user_login'), # 登录
    path('api/journal/<int:period_number>/update/', views.update_journal_field, name='update_journal_field'), # 更新期刊字段
    path('api/journal/<int:period_number>/create/', views.create_journal, name='create_journal'), # 创建期刊
    path('api/journal/<int:period_number>/clear/', views.clear_journal_data, name='clear_journal_data'), # 清除期刊数据
    path('api/journal/<int:period_number>/append_files/', views.append_journal_files, name='append_journal_files'), # 追加期刊文件
    path('api/journal/<int:period_number>/data/', views.get_journal_data, name='get_journal_data'),
    path('api/journal/<int:period_number>/edition/', views.batch_update_edition, name='batch_update_edition'), # 批量更新版次
    path('api/journal/', views.get_journal_content, name='get_journal_content'), # 获取期刊内容
    path('api/invoice/update/', views.update_invoice, name='update_invoice'), # 更新发票
    path('api/invoice/create/', views.create_invoice, name='create_invoice'), # 创建发票    
    path('api/invoice/data/', views.get_invoice_data, name='get_invoice_data'), # 获取发票数据  
    path('api/invoice/delete/', views.delete_invoice, name='delete_invoice'), # 删除发票
    path('api/invoice/clear/', views.clear_invoice_data, name='clear_invoice_data'), # 清除发票数据
    path('api/invoice/import/', views.import_invoice_data, name='import_invoice_data'), # 导入发票数据
    path('api/schedule/data/', views.get_article_schedule_data, name='get_article_schedule_data'),
    path('api/schedule/update/', views.update_article_schedule, name='update_article_schedule'), # 更新文章进度
    path('api/schedule/create/', views.create_article_schedule, name='create_article_schedule'), # 创建文章进度
    path('api/schedule/delete/', views.delete_article_schedule, name='delete_article_schedule'), # 删除文章进度
    path('api/schedule/clear/', views.clear_article_schedule_data, name='clear_article_schedule_data'), # 清除文章进度数据
    path('api/schedule/import/', views.import_article_schedule_data, name='import_article_schedule_data'), # 导入文章进度数据
    path('api/journal/period-mapping/', views.get_period_mapping, name='get_period_mapping'),
    path('api/journal/period-mapping/update/', views.update_period_mapping, name='update_period_mapping'), # 更新期刊期数映射
    path('api/journal/<int:period>/data/', views.import_files, name='import_files'), # 导入期刊文件
    path('api/journal/<int:period_number>/delete/', views.delete_journal, name='delete_journal'), # 删除期刊
    path('api/template/load/', views.load_template, name='load_template'),
    path('api/template/save/', views.save_template, name='save_template'), # 保存邮件模板
    path('api/notification/generate/', views.generate_notification, name='generate_notification'),
    path('api/notification/download/<str:filename>/', views.download_notification, name='download_notification'), # 下载通知文件
    path('api/notification/clear_files/', views.clear_notification_files, name='clear_notification_files'),
    # 更新日志
    path('api/update-log/latest/', views.get_latest_update_log, name='get_latest_update_log'),
    # 期刊进度汇总
    path('api/journal-progress-summary/', views.get_journal_progress_summary, name='get_journal_progress_summary'),
    # 待办事项相关路由
    path('api/todos/', views.todo_list_view, name='todo_list'), # 获取待办事项
    path('api/todos/<int:todo_id>/', views.todo_detail_view, name='todo_detail'), # 获取待办事项详情
    path('api/todos/<int:todo_id>/status/', views.todo_status_view, name='todo_status'),
    # 参考文献纠错相关路由
    path('api/reference/check/', views.check_references, name='check_references'), # 检查参考文献
    
    # 邮件模板管理API
    path('api/email-templates/', views.get_email_templates, name='get_email_templates'),
    path('api/email-templates/create/', views.create_email_template, name='create_email_template'), # 创建邮件模板  
    path('api/email-templates/<int:template_id>/update/', views.update_email_template, name='update_email_template'), # 更新邮件模板
    path('api/email-templates/<int:template_id>/delete/', views.delete_email_template, name='delete_email_template'), # 删除邮件模板
    
    # 联系人管理API
    path('api/recipients/', views.get_recipients, name='get_recipients'), # 获取联系人
    path('api/recipients/create/', views.create_recipient, name='create_recipient'), # 创建联系人
    path('api/recipients/<int:recipient_id>/update/', views.update_recipient, name='update_recipient'), # 更新联系人
    path('api/recipients/<int:recipient_id>/delete/', views.delete_recipient, name='delete_recipient'), # 删除联系人
    path('api/recipients/batch-delete/', views.batch_delete_recipients, name='batch_delete_recipients'), # 批量删除联系人
    path('api/recipients/batch-update-group/', views.batch_update_group, name='batch_update_group'), # 批量更新联系人分组
    path('api/recipients/import/', views.import_recipients, name='import_recipients'), # 导入联系人
    # 多分组追加/移除（不覆盖）
    path('api/recipients/append-to-group/', views.append_to_group, name='append_to_group'), # 追加联系人到分组
    path('api/recipients/remove-from-group/', views.remove_from_group, name='remove_from_group'), # 从分组中移除联系人
    # 一次性数据清理：未分组唯一性
    path('api/recipients/cleanup-ungrouped-invariant/', views.cleanup_ungrouped_invariant, name='cleanup_ungrouped_invariant'), # 清理未分组唯一性  
    
    # 分组管理API
    path('api/groups/', views.get_groups, name='get_groups'), # 获取分组
    path('api/groups/create/', views.create_group, name='create_group'), # 创建分组             
    path('api/groups/rename/', views.rename_group, name='rename_group'), # 重命名分组
    path('api/groups/delete/', views.delete_group, name='delete_group'), # 删除分组
] 