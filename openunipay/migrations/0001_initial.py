# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-31 02:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AliPayOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('out_trade_no', models.CharField(db_index=True, editable=False, max_length=32, verbose_name=b'\xe5\x95\x86\xe6\x88\xb7\xe8\xae\xa2\xe5\x8d\x95\xe5\x8f\xb7')),
                ('subject', models.CharField(editable=False, max_length=128, verbose_name=b'\xe5\x95\x86\xe5\x93\x81\xe5\x90\x8d\xe7\xa7\xb0')),
                ('body', models.CharField(editable=False, max_length=512, verbose_name=b'\xe5\x95\x86\xe5\x93\x81\xe8\xaf\xa6\xe6\x83\x85')),
                ('total_fee', models.DecimalField(decimal_places=2, editable=False, max_digits=6, verbose_name=b'\xe6\x80\xbb\xe9\x87\x91\xe9\xa2\x9d(\xe5\x8d\x95\xe4\xbd\x8d:\xe5\x85\x83)')),
                ('it_b_pay', models.CharField(editable=False, max_length=19, verbose_name=b'\xe4\xba\xa4\xe6\x98\x93\xe6\x9c\x89\xe6\x95\x88\xe6\x9c\x9f')),
                ('date_create', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
            ],
            options={
                'verbose_name': '\u652f\u4ed8\u5b9d\u8ba2\u5355',
                'verbose_name_plural': '\u652f\u4ed8\u5b9d\u8ba2\u5355',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('orderno', models.CharField(editable=False, max_length=50, primary_key=True, serialize=False, verbose_name='\u8ba2\u5355\u53f7')),
                ('user', models.CharField(blank=True, max_length=50, null=True, verbose_name='\u7528\u6237\u6807\u8bc6')),
                ('product_desc', models.CharField(max_length=128, verbose_name='\u5546\u54c1\u63cf\u8ff0')),
                ('product_detail', models.TextField(max_length=1000, verbose_name='\u5546\u54c1\u8be6\u60c5')),
                ('fee', models.DecimalField(decimal_places=0, max_digits=6, verbose_name='\u91d1\u989d(\u5355\u4f4d:\u5206)')),
                ('attach', models.CharField(blank=True, max_length=127, null=True, verbose_name='\u9644\u52a0\u6570\u636e')),
                ('dt_start', models.DateTimeField(editable=False, verbose_name='\u4ea4\u6613\u5f00\u59cb\u65f6\u95f4')),
                ('dt_end', models.DateTimeField(editable=False, verbose_name='\u4ea4\u6613\u5931\u6548\u65f6\u95f4')),
                ('dt_pay', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='\u4ed8\u6b3e\u65f6\u95f4')),
                ('paied', models.BooleanField(default=False, editable=False, verbose_name='\u5df2\u6536\u6b3e')),
                ('lapsed', models.BooleanField(default=False, editable=False, verbose_name='\u5df2\u5931\u6548')),
                ('payway', models.CharField(choices=[(b'WEIXIN', '\u5fae\u4fe1\u652f\u4ed8'), (b'ALI', '\u652f\u4ed8\u5b9d\u652f\u4ed8')], default=b'WEIXIN', max_length=10, verbose_name='\u652f\u4ed8\u65b9\u5f0f')),
                ('date_create', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('date_update', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
            ],
            options={
                'verbose_name': '\u4ed8\u6b3e\u5355',
                'verbose_name_plural': '\u4ed8\u6b3e\u5355',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('productid', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='\u5546\u54c1ID')),
                ('product_desc', models.CharField(max_length=128, verbose_name='\u5546\u54c1\u63cf\u8ff0')),
                ('product_detail', models.TextField(max_length=1000, verbose_name='\u5546\u54c1\u8be6\u60c5')),
                ('fee', models.DecimalField(decimal_places=0, max_digits=6, verbose_name='\u91d1\u989d(\u5355\u4f4d:\u5206)')),
                ('date_create', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('date_update', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
            ],
            options={
                'verbose_name': '\u5546\u54c1',
                'verbose_name_plural': '\u5546\u54c1',
            },
        ),
        migrations.CreateModel(
            name='WeiXinOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appid', models.CharField(editable=False, max_length=32, verbose_name='\u516c\u4f17\u8d26\u53f7ID')),
                ('mch_id', models.CharField(editable=False, max_length=32, verbose_name='\u5546\u6237\u53f7')),
                ('body', models.CharField(editable=False, max_length=128, verbose_name='\u5546\u54c1\u63cf\u8ff0')),
                ('attach', models.CharField(blank=True, editable=False, max_length=127, null=True, verbose_name='\u9644\u52a0\u6570\u636e')),
                ('out_trade_no', models.CharField(db_index=True, editable=False, max_length=32, verbose_name='\u5546\u6237\u8ba2\u5355\u53f7')),
                ('fee_type', models.CharField(editable=False, max_length=16, verbose_name='\u8d27\u5e01\u7c7b\u578b')),
                ('total_fee', models.PositiveIntegerField(editable=False, verbose_name='\u603b\u91d1\u989d')),
                ('spbill_create_ip', models.CharField(editable=False, max_length=16, verbose_name='\u7ec8\u7aefIP')),
                ('time_start', models.CharField(editable=False, max_length=14, verbose_name='\u4ea4\u6613\u8d77\u59cb\u65f6\u95f4')),
                ('time_expire', models.CharField(editable=False, max_length=14, verbose_name='\u4ea4\u6613\u7ed3\u675f\u65f6\u95f4')),
                ('notify_url', models.CharField(editable=False, max_length=256, verbose_name='\u901a\u77e5\u5730\u5740')),
                ('trade_type', models.CharField(editable=False, max_length=16, verbose_name='\u4ea4\u6613\u7c7b\u578b')),
                ('openid', models.CharField(blank=True, editable=False, max_length=128, null=True, verbose_name='\u7528\u6237\u6807\u8bc6(openId)')),
            ],
            options={
                'verbose_name': '\u5fae\u4fe1\u7edf\u4e00\u8ba2\u5355',
                'verbose_name_plural': '\u5fae\u4fe1\u7edf\u4e00\u8ba2\u5355',
            },
        ),
        migrations.CreateModel(
            name='WeiXinQRPayEntity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appid', models.CharField(editable=False, max_length=32, verbose_name='\u516c\u4f17\u8d26\u53f7ID')),
                ('mch_id', models.CharField(editable=False, max_length=32, verbose_name='\u5546\u6237\u53f7')),
                ('time_stamp', models.CharField(editable=False, max_length=10, verbose_name='\u65f6\u95f4\u6233')),
                ('product_id', models.CharField(editable=False, max_length=32, verbose_name='\u5546\u54c1ID')),
            ],
            options={
                'verbose_name': '\u5fae\u4fe1\u626b\u7801\u652f\u4ed8-\u4e8c\u7ef4\u7801URL',
                'verbose_name_plural': '\u5fae\u4fe1\u626b\u7801\u652f\u4ed8-\u4e8c\u7ef4\u7801URL',
            },
        ),
        migrations.CreateModel(
            name='WeiXinQRPayRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appid', models.CharField(editable=False, max_length=32, verbose_name='\u516c\u4f17\u8d26\u53f7ID')),
                ('mch_id', models.CharField(editable=False, max_length=32, verbose_name='\u5546\u6237\u53f7')),
                ('openid', models.CharField(editable=False, max_length=128, verbose_name='\u7528\u6237\u6807\u8bc6')),
                ('product_id', models.CharField(editable=False, max_length=32, verbose_name='\u5546\u54c1ID')),
            ],
            options={
                'verbose_name': '\u5fae\u4fe1\u626b\u7801\u652f\u4ed8-\u626b\u7801\u7eaa\u5f55',
                'verbose_name_plural': '\u5fae\u4fe1\u626b\u7801\u652f\u4ed8-\u626b\u7801\u7eaa\u5f55',
            },
        ),
        migrations.CreateModel(
            name='AliPayResult',
            fields=[
                ('order', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='pay_result', serialize=False, to='openunipay.AliPayOrder')),
                ('notify_time', models.CharField(blank=True, editable=False, max_length=19, null=True, verbose_name='\u901a\u77e5\u65f6\u95f4')),
                ('notify_type', models.CharField(blank=True, editable=False, max_length=50, null=True, verbose_name='\u901a\u77e5\u7c7b\u578b')),
                ('notify_id', models.CharField(blank=True, editable=False, max_length=50, null=True, verbose_name='\u901a\u77e5\u6821\u9a8cID')),
                ('out_trade_no', models.CharField(blank=True, editable=False, max_length=32, null=True, verbose_name='\u5546\u6237\u8ba2\u5355\u53f7')),
                ('subject', models.CharField(blank=True, editable=False, max_length=128, null=True, verbose_name='\u5546\u54c1\u540d\u79f0')),
                ('trade_no', models.CharField(blank=True, editable=False, max_length=64, null=True, verbose_name='\u652f\u4ed8\u5b9d\u4ea4\u6613\u53f7')),
                ('trade_status', models.CharField(blank=True, editable=False, max_length=16, null=True, verbose_name='\u4ea4\u6613\u72b6\u6001')),
                ('seller_id', models.CharField(blank=True, editable=False, max_length=30, null=True, verbose_name='\u5356\u5bb6\u652f\u4ed8\u5b9d\u7528\u6237\u53f7')),
                ('seller_email', models.CharField(blank=True, editable=False, max_length=100, null=True, verbose_name='\u5356\u5bb6\u652f\u4ed8\u5b9d\u8d26\u53f7')),
                ('buyer_id', models.CharField(blank=True, editable=False, max_length=30, null=True, verbose_name='\u4e70\u5bb6\u652f\u4ed8\u5b9d\u7528\u6237\u53f7')),
                ('buyer_email', models.CharField(blank=True, editable=False, max_length=100, null=True, verbose_name='\u4e70\u5bb6\u652f\u4ed8\u5b9d\u8d26\u53f7  ')),
                ('total_fee', models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=6, null=True, verbose_name='\u603b\u91d1\u989d(\u5355\u4f4d:\u5143)')),
            ],
        ),
        migrations.CreateModel(
            name='WeiXinPayResult',
            fields=[
                ('order', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='pay_result', serialize=False, to='openunipay.WeiXinOrder')),
                ('prepayid', models.CharField(blank=True, db_index=True, editable=False, max_length=64, null=True, verbose_name='\u9884\u652f\u4ed8\u4ea4\u6613\u4f1a\u8bdd\u6807\u8bc6')),
                ('openid', models.CharField(blank=True, editable=False, max_length=128, null=True, verbose_name='\u7528\u6237\u6807\u8bc6(openId)')),
                ('bank_type', models.CharField(blank=True, editable=False, max_length=16, null=True, verbose_name='\u4ed8\u6b3e\u94f6\u884c')),
                ('total_fee', models.SmallIntegerField(blank=True, editable=False, null=True, verbose_name='\u603b\u91d1\u989d')),
                ('attach', models.CharField(blank=True, editable=False, max_length=128, null=True, verbose_name='\u5546\u6237\u9644\u52a0\u6570\u636e')),
                ('tradestate', models.CharField(blank=True, editable=False, max_length=32, null=True, verbose_name='\u4ea4\u6613\u72b6\u6001')),
                ('tradestatedesc', models.CharField(blank=True, editable=False, max_length=256, null=True, verbose_name='\u4ea4\u6613\u72b6\u6001\u63cf\u8ff0')),
            ],
        ),
    ]
