
from django.contrib import admin
from django.urls import path, re_path
from administer import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('index', views.index),
    path('index.html', views.index),
    path('login.html', views.login),
    path('login/', views.login),
    path('register.html', views.register),
    path('register/', views.register),

    # 用户路由
    path('shop.html', views.shop),
    path('shop/', views.shop),
    path('userhome.html', views.userhome),
    path('userhome/', views.userhome),
    path('userorder.html', views.userorder),
    path('userorder/', views.userorder),

    # 门店店长路由
    path('shopmanage-home.html', views.shopmanage_home),
    path('shopmanege-home/', views.shopmanage_home),
    path('shopmanage-userorder.html', views.shopmanage_userorder),
    path('shopmanege-userorder/', views.shopmanage_userorder),
    path('shopmanage-shoporder.html', views.shopmanage_shoporder),
    path('shopmanege-shoporder/', views.shopmanage_shoporder),
    path('shopmanage-stock.html', views.shopmanage_stock),
    path('shopmanege-stock/', views.shopmanage_stock),

    # 仓库管理路由
    path('warehouse-home.html', views.warehouse_home),
    path('warehouse-home/', views.warehouse_home),
    path('warehouse-shoporder.html', views.warehouse_order),
    path('warehouse-shoporder/', views.warehouse_order),
    path('warehouse-stock.html', views.warehouse_stock),
    path('warehouse-stock/', views.warehouse_stock),

    # 电商部门
    path('online-home.html', views.online_home),
    path('online-home/', views.online_home),
    path('online-order.html', views.online_order),
    path('online-order/', views.online_order),

    re_path(r'manage_(\w+)', views.manage_),
    path('403.html', views.no_right),
    path('no_type.html', views.no_type),
    path('not_enough.html', views.not_enough),
    path('not_enough_w.html', views.not_enough_w),

    # 调试专用路由
    path('d', views.default_database),      # 数据库初始化
    path('c', views.check_stock),      # 库存同步

]

# handler404 = views.page_not_found
