# Generated migration for Todo model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qikan', '0015_merge_first_second_proof_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Todo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField(verbose_name='任务内容')),
                ('assignee', models.CharField(choices=[('孙航', '孙航'), ('李彦燕', '李彦燕'), ('陈玉忠', '陈玉忠'), ('孔源博', '孔源博'), ('新用户1', '新用户1'), ('新用户2', '新用户2')], max_length=20, verbose_name='添加人')),
                ('priority', models.CharField(choices=[('low', '低'), ('medium', '中'), ('high', '高')], default='medium', max_length=10, verbose_name='优先级')),
                ('status', models.CharField(choices=[('in_progress', '进行中'), ('completed', '已完成')], default='in_progress', max_length=20, verbose_name='状态')),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='截止日期')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '待办事项',
                'verbose_name_plural': '待办事项',
                'db_table': 'qikan_todo',
                'ordering': ['-created_at'],
            },
        ),
    ]
