from django.db import models


# 用户账户
class User(models.Model):
    u_id = models.AutoField(primary_key=True)   # 自动填写 （ 自增数字）主键
    username = models.CharField(max_length=32, null=False)  # 字符串，不能为空
    password = models.CharField(max_length=64, null=False)
    u_type = models.CharField(max_length=32, null=False, default='用户')  # 字符串，默认值'用户'
    addr = models.CharField(max_length=64, null=True, default=None)     # 字符串 默认值None
    tel = models.CharField(max_length=32, null=True, default=None)
    email = models.EmailField(max_length=32, null=True, default=None)
# 用户账户


# 商品信息
class Goods(models.Model):
    g_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, null=False)
    price = models.IntegerField(null=False)     # 数字类型， 不能为空
# 商品信息


# 门店信息
class Shop(models.Model):
    s_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32, null=False)
    location = models.CharField(max_length=64, null=False)
    manager = models.ForeignKey('User', to_field='u_id', on_delete=models.PROTECT)      # 外键关联user的u_id
# 门店信息


# 用户订单
class UserOrder(models.Model):
    goods_id = models.ForeignKey('Goods', to_field='g_id', on_delete=models.PROTECT)
    user_id = models.ForeignKey('User', to_field='u_id', on_delete=models.PROTECT)
    amount = models.IntegerField(null=False)
    time = models.DateTimeField(auto_now_add=True, null=False)              # 时间类型，自动生成创建时间
    price = models.IntegerField(null=False)
    status = models.CharField(max_length=32, null=False)
    method = models.CharField(max_length=32, null=False, default='发货')
    remark = models.CharField(max_length=32, null=False, default='无')
# 用户订单


# 门店订单
class ShopOrder(models.Model):
    goods_id = models.ForeignKey('Goods', to_field='g_id', on_delete=models.PROTECT)
    shop_id = models.ForeignKey('Shop', to_field='s_id', on_delete=models.PROTECT)
    amount = models.IntegerField(null=False)
    time = models.DateTimeField(auto_now_add=True, null=False)
    status = models.CharField(max_length=32, null=False)
# 门店订单


# 门店库存
class ShopStock(models.Model):
    shop_id = models.ForeignKey('Shop', to_field='s_id', on_delete=models.PROTECT)
    goods_id = models.ForeignKey('Goods', to_field='g_id', on_delete=models.PROTECT)
    amount = models.IntegerField(null=False)
# 门店库存


# 仓库库存
class WarehouseStock(models.Model):
    goods_id = models.ForeignKey('Goods', to_field='g_id', on_delete=models.PROTECT)
    amount = models.IntegerField(null=False)
# 仓库库存


# 仓库进货
class Replenish(models.Model):
    goods_id = models.ForeignKey('Goods', to_field='g_id', on_delete=models.PROTECT)
    amount = models.IntegerField(null=False)
    price = models.IntegerField(null=False)
# 仓库进货


# 流水账
class Tally(models.Model):
    t_type = models.CharField(max_length=32, null=False)
    goods_id = models.ForeignKey('Goods', to_field='g_id', on_delete=models.PROTECT)
    amount = models.IntegerField(null=False)
    order_id = models.IntegerField(null=False)
    time = models.DateTimeField(auto_now_add=True, null=False)
    price = models.IntegerField(null=False)
# 流水账
