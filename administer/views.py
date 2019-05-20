from django.shortcuts import render, HttpResponse, redirect
from administer import models, check_psw


# 主页请求处理
def index(request):
    return render(request, 'index.html')


# 登录界面请求处理
def login(request):
    if request.method == 'POST':
        print('sth post')
        username = request.POST.get('user_name')
        password = request.POST.get('password')
        password = check_psw.check(username, password)
        user = models.User.objects.filter(username=username).first()
        if user is None:
            err_msg = '该用户不存在'
            return render(request, 'login.html', {'err_msg': err_msg})
        else:
            if password == user.password:
                usertype = user.u_type
                if usertype == '用户':
                    res = redirect('/shop.html')
                    res.set_cookie('username', username)
                    res.set_cookie('usertype', '用户'.encode('utf-8'))
                    return res
                elif usertype == '门店店长':
                    res = redirect('/shopmanage-home.html')
                    res.set_cookie('username', username)
                    res.set_cookie('usertype', '门店店长'.encode('utf-8'))
                    return res
                elif usertype == '仓库管理员':
                    res = redirect('/warehouse-home.html')
                    res.set_cookie('username', username)
                    res.set_cookie('usertype', '仓库管理员'.encode('utf-8'))
                    return res
                elif usertype == '会计':
                    res = redirect('/manage_home')
                    res.set_cookie('username', username)
                    res.set_cookie('usertype', '会计'.encode('utf-8'))
                    return res
                elif usertype == '电商部门':
                    res = redirect('/online-home')
                    res.set_cookie('username', username)
                    res.set_cookie('usertype', '电商部门'.encode('utf-8'))
                    return res
                elif usertype == 'worldmaker':
                    res = redirect('/manage_home')
                    res.set_cookie('username', username)
                    res.set_cookie('usertype', 'world maker'.encode('utf-8'))
                    return res
                else:
                    return redirect('/no_type.html')

            else:
                err_msg = '用户名与密码不匹配，请重试'
                return render(request, 'login.html', {'err_msg': err_msg})
    return render(request, 'login.html')


# 注册界面请求处理
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        username = get_post(request, 'username')
        temp = models.User.objects.filter(username=username)
        if len(temp) > 0:
            err_msg = '该用户已存在'
            return render(request, 'register.html', {'err_msg': err_msg})
        else:
            password = get_post(request, 'password')
            u_type = '用户'
            addr = get_post(request, 'addr')
            if addr == '':
                addr = None
            tel = get_post(request, 'tel')
            if tel == '':
                tel = None
            email = get_post(request, 'email')
            if email == '':
                email = None
            password = check_psw.check(username, password)
            models.User.objects.create(username=username, password=password, u_type=u_type, addr=addr,
                                       tel=tel, email=email)
            return redirect('/index')


# 购物界面请求处理
def shop(request):
    if request.method == 'GET':
        username = '请登录'
        usertype = ''
        data_list = []
        goods_list = models.Goods.objects.all()
        for item in goods_list:
            temp = {'g_id': item.g_id,
                    'name': item.name,
                    'price': item.price,
                    }
            data_list.append(temp)
            username = request.COOKIES.get('username')
        if username is not None:
            usertype = request.COOKIES.get('usertype')
            usertype = s_to_b(usertype)
        shop_list = []
        shop_set = models.Shop.objects.all()
        for item in shop_set:
            shop_list.append(item.name)
        return render(request, 'shop.html', {'data_list': data_list, 'shop_list': shop_list, 'username': username, 'usertype': usertype})
    elif request.method == 'POST':
        username = request.COOKIES.get('username', None)
        if username is None:
            return redirect('/login.html')
        else:
            goodsname = request.POST.get('goodsname', None)
            amount = request.POST.get('account', None)
            goods_id = models.Goods.objects.filter(name=goodsname).first()
            g_price = goods_id.price
            user_id = models.User.objects.filter(username=username).first()
            price = int(amount) * g_price
            method_n = get_post(request, 'method')
            if method_n == '1':
                method = '发货'
                remark = '无'
                status = '已付款，等待发货'
            else:
                method = '门店自提'
                remark = request.POST.get('shop', None)
                status = '等待自提'

            # 更新库存
            if method == '发货':
                goods = models.Goods.objects.filter(name=goodsname).first()
                obj = models.WarehouseStock.objects.filter(goods_id=goods).first()
                amount = int(amount)
                stock = obj.amount - amount
                if stock < 0:
                    print('库存不足')
                    return redirect('/not_enough.html')
                else:
                    obj.amount = stock
                    obj.save()
            elif method == '门店自提':
                goods = models.Goods.objects.filter(name=goodsname).first()
                shop = models.Shop.objects.filter(name=remark).first()
                obj = models.ShopStock.objects.filter(goods_id=goods, shop_id=shop).first()
                amount = int(amount)
                stock = obj.amount - amount
                if stock < 0:
                    print('库存不足')
                    return redirect('/not_enough.html')
                else:
                    print(stock)
                    obj.amount = stock
                    obj.save()
            models.UserOrder.objects.create(goods_id=goods_id, user_id=user_id, amount=amount, price=price,
                                            status=status, method=method, remark=remark)
            return redirect('/userorder.html')


# 用户我的订单请求处理
def userorder(request):
    if request.method == 'GET':
        username = request.COOKIES.get('username')
        if username is None:
            return redirect('/login.html')
        else:
            data_list = []
            usertype = request.COOKIES.get('usertype')
            usertype = s_to_b(usertype)
            user = models.User.objects.filter(username=username).first()
            order_list = models.UserOrder.objects.filter(user_id=user).all()
            for item in order_list:
                temp = {'id': item.id,
                        'goods_name': item.goods_id.name,
                        'amount': item.amount,
                        'time': item.time,
                        'price': item.price,
                        'status': item.status,
                        'method': item.method
                        }
                data_list.append(temp)
            return render(request, 'userorder.html', {'data_list': data_list, 'username': username, 'usertype': usertype})
    elif request.method == 'POST':
        order_id = request.POST.get('userorder', None)
        models.UserOrder.objects.filter(id=order_id).update(status='已收货')
        return redirect('/userorder.html')


# 用户个人中心请求处理
def userhome(request):
    username = request.COOKIES.get('username')
    if username is None:
        return redirect('/login.html')
    else:
        usertype = request.COOKIES.get('usertype')
        usertype = s_to_b(usertype)
        user = models.User.objects.filter(username=username).first()
        data_dict = {
                    'username': user.username,
                    'password': user.password,
                    'addr': user.addr,
                    'tel': user.tel,
                    'email': user.email
                    }
        return render(request, 'userhome.html', {'data_list': data_dict, 'username': username, 'usertype': usertype})


# 门店管理用户订单的请求处理
def shopmanage_userorder(request):
    if request.method == 'GET':
        usertype = request.COOKIES.get('usertype')
        if usertype is None:
            return redirect('403.html')
        usertype = s_to_b(usertype)
        if usertype != '门店店长':
            return redirect('403.html')
        else:
            username = request.COOKIES.get('username')
            user = models.User.objects.filter(username=username).first()
            manager = models.Shop.objects.filter(manager=user).first()
            if manager is None:
                return redirect('/403.html')
            else:
                data_list = []
                userorder_list = models.UserOrder.objects.filter(remark=manager.name)
                for item in userorder_list:
                    temp = {'id': item.id,
                            'goods_name': item.goods_id.name,
                            'user_id': item.user_id.u_id,
                            'amount': item.amount,
                            'time': item.time,
                            'price': item.price,
                            'status': item.status
                            }
                    data_list.append(temp)
                return render(request, 'shopmanage-userorder.html', {'data_list': data_list, 'username': username,
                                                                     'usertype': usertype})
    if request.method == 'POST':
        order_id = request.POST.get('userorder', None)
        models.UserOrder.objects.filter(id=order_id).update(status='自提完成')
        return redirect('/shopmanage-userorder.html')


# 门店管理进货订单的请求处理
def shopmanage_shoporder(request):
    if request.method == 'GET':
        usertype = request.COOKIES.get('usertype')
        if usertype is None:
            return redirect('403.html')
        usertype = s_to_b(usertype)
        if usertype != '门店店长':
            return redirect('403.html')
        else:
            data_list = []
            username = request.COOKIES.get('username')
            user = models.User.objects.filter(username=username).first()
            shop = models.Shop.objects.filter(manager=user).first()
            if shop is None:
                return redirect('/403.html')
            else:
                shop_order_list = models.ShopOrder.objects.filter(shop_id=shop).all()
                for item in shop_order_list:
                    temp = {'id': item.id,
                            'goods_name': item.goods_id.name,
                            'amount': item.amount,
                            'time': item.time,
                            'status': item.status
                            }
                    data_list.append(temp)
                return render(request, 'shopmanage-shoporder.html', {'data_list': data_list, 'username': username,
                                                                     'usertype': usertype})
    elif request.method == 'POST':
        username = request.COOKIES.get('username')
        user = models.User.objects.filter(username=username).first()
        shop = models.Shop.objects.filter(manager=user).first()
        shop_order = request.POST.get('shoporder', None)
        models.ShopOrder.objects.filter(id=shop_order).update(status='已收货')
        order = models.ShopOrder.objects.filter(id=shop_order).first()
        goods = order.goods_id
        amount = order.amount
        o_amount = models.ShopStock.objects.filter(shop_id=shop, goods_id=goods).first().amount
        amount = amount + o_amount
        models.ShopStock.objects.filter(goods_id=goods, shop_id=shop).update(amount=amount)
        return redirect('/shopmanage-shoporder.html')


# 门店管理修改库存的请求处理
def shopmanage_stock(request):
    if request.method == 'GET':
        usertype = request.COOKIES.get('usertype')
        if usertype is None:
            return redirect('403.html')
        usertype = s_to_b(usertype)
        if usertype != '门店店长':
            return redirect('403.html')
        else:
            data_list = []
            username = request.COOKIES.get('username')
            user = models.User.objects.filter(username=username).first()
            shop = models.Shop.objects.filter(manager=user).first()
            if shop is None:
                return redirect('/403.html')
            else:
                shop_stock_list = models.ShopStock.objects.filter(shop_id=shop).all()
                for item in shop_stock_list:
                    temp = {'goods_name': item.goods_id.name,
                            'shop_id': item.shop_id.s_id,
                            'amount': item.amount
                            }
                    data_list.append(temp)
                return render(request, 'shopmanage-stock.html', {'username': username, 'usertype': usertype,
                                                                 'data_list': data_list})
    if request.method == 'POST':
        username = request.COOKIES.get('username')
        user = models.User.objects.filter(username=username).first()
        shop = models.Shop.objects.filter(manager=user).first()
        method = request.POST.get('method', None)
        goods_name = request.POST.get('goods_id', None)
        goods = models.Goods.objects.filter(name=goods_name).first()
        amount = request.POST.get('amount', None)
        if method == 'change':
            models.ShopStock.objects.filter(goods_id=goods, shop_id=shop).update(amount=amount)
            return redirect('/shopmanage-stock.html')
        elif method == 'add':
            status = '等待发货'
            models.ShopOrder.objects.create(goods_id=goods, shop_id=shop, amount=amount, status=status)

            return redirect('/shopmanage-shoporder.html')


# 门店管理首页请求处理
def shopmanage_home(request):
    if request.method == 'GET':
        usertype = request.COOKIES.get('usertype')
        if usertype is None:
            return redirect('403.html')
        usertype = s_to_b(usertype)
        if usertype != '门店店长':
            return redirect('403.html')
        else:
            username = request.COOKIES.get('username')
            return render(request, 'shopmanage-home.html', {'username': username, 'usertype': usertype})


# 仓库管理首页
def warehouse_home(request):
    if request.method == 'GET':
        usertype = request.COOKIES.get('usertype')
        if usertype is None:
            return redirect('403.html')
        usertype = s_to_b(usertype)
        if usertype != '仓库管理员':
            return redirect('403.html')
        else:
            username = request.COOKIES.get('username')
            return render(request, 'warehouse-home.html', {'username': username, 'usertype': usertype})


# 门店订单请求
def warehouse_order(request):
    if request.method == 'GET':
        usertype = request.COOKIES.get('usertype')
        if usertype is None:
            return redirect('403.html')
        usertype = s_to_b(usertype)
        if usertype != '仓库管理员':
            return redirect('403.html')
        else:
            username = request.COOKIES.get('username')
            data_list = []
            shoporder_list = models.ShopOrder.objects.all()
            for item in shoporder_list:
                temp = {'id': item.id,
                        'goods_name': item.goods_id.name,
                        'shop_id': item.shop_id.s_id,
                        'amount': item.amount,
                        'shop_name': item.shop_id.name,
                        'time': item.time,
                        'status': item.status
                        }
                data_list.append(temp)
            return render(request, 'warehouse-shoporder.html', {'data_list': data_list, 'username': username,
                                                                'usertype': usertype})
    if request.method == 'POST':
        order_id = request.POST.get('shoporder', None)
        order = models.ShopOrder.objects.filter(id=order_id).first()
        amount = order.amount
        print(amount)
        obj = models.WarehouseStock.objects.filter(goods_id=order.goods_id).first()
        amount = int(amount)
        stock = obj.amount - amount
        if stock < 0:
            print('库存不足')
            return redirect('/not_enough_w.html')
        else:
            obj.amount = stock
            obj.save()
        models.ShopOrder.objects.filter(id=order_id).update(status='已发货，等待收货')
        return redirect('/warehouse-shoporder.html')


# 仓库库存
def warehouse_stock(request):
    if request.method == 'GET':
        usertype = request.COOKIES.get('usertype')
        if usertype is None:
            return redirect('403.html')
        usertype = s_to_b(usertype)
        if usertype != '仓库管理员':
            return redirect('403.html')
        else:
            data_list = []
            username = request.COOKIES.get('username')
            shop_stock_list = models.WarehouseStock.objects.filter().all()
            for item in shop_stock_list:
                temp = {'goods_name': item.goods_id.name,
                        'amount': item.amount
                        }
                data_list.append(temp)
            return render(request, 'warehouse-stock.html', {'username': username, 'usertype': usertype,
                                                            'data_list': data_list})
    if request.method == 'POST':
        method = request.POST.get('method', None)
        goods_name = request.POST.get('goods_id', None)
        goods = models.Goods.objects.filter(name=goods_name).first()
        amount = request.POST.get('amount', None)
        if method == 'change':
            models.WarehouseStock.objects.filter(goods_id=goods).update(amount=amount)
            return redirect('/warehouse-stock.html')
        elif method == 'add':
            o_amount = models.WarehouseStock.objects.filter(goods_id=goods).first().amount
            amount = request.POST.get('amount', None)
            amount = int(amount)
            amount = amount + o_amount
            models.WarehouseStock.objects.filter(goods_id=goods).update(amount=amount)
            return redirect('/warehouse-stock.html')


# 电商首页
def online_home(request):
    if request.method == 'GET':
        usertype = request.COOKIES.get('usertype')
        if usertype is None:
            return redirect('403.html')
        usertype = s_to_b(usertype)
        if usertype != '电商部门':
            return redirect('403.html')
        else:
            username = request.COOKIES.get('username')
            return render(request, 'online-home.html', {'username': username, 'usertype': usertype})


# 电商订单
def online_order(request):
    if request.method == 'GET':
        usertype = request.COOKIES.get('usertype')
        if usertype is None:
            return redirect('403.html')
        usertype = s_to_b(usertype)
        if usertype != '电商部门':
            return redirect('403.html')
        else:
            data_list = []
            username = request.COOKIES.get('username')
            userorder_list = models.UserOrder.objects.filter(method='发货')
            for item in userorder_list:
                temp = {'id': item.id,
                        'goods_id': item.goods_id.g_id,
                        'user_id': item.user_id.username,
                        'amount': item.amount,
                        'time': item.time,
                        'status': item.status
                        }
                data_list.append(temp)
            return render(request, 'online-order.html', {'data_list': data_list, 'username': username,
                                                         'usertype': usertype})
    if request.method == 'POST':
        order_id = request.POST.get('userorder', None)
        models.UserOrder.objects.filter(id=order_id).update(status='已发货，等待收货')
        return redirect('/online-order.html')


# 电商库存
def online_stock(request):
    pass


# 后台管理所有请求处理
def manage_(request, page):
    usertype = request.COOKIES.get('usertype')
    if usertype is None:
        return redirect('403.html')
    usertype = s_to_b(usertype)
    if usertype != 'world maker':
        return redirect('403.html')
    else:
        username = request.COOKIES.get('username')
        data_list = []
        err_msg = ''
        if page == 'home':
            return render(request, 'manage-home.html', {'username': username, 'usertype': usertype})
        # 点击用户管理
        elif page == 'user':
            table = {'u_id': '用户ID',
                     'username': '用户名',
                     'password': '密码',
                     'u_type': '用户类型',
                     'addr': '地址',
                     'tel': '联系电话',
                     'email': 'E-mail'}
            user_list = models.User.objects.all()
            for item in user_list:
                temp = {'u_id': item.u_id,
                        'username': item.username,
                        'password': item.password,
                        'u_type': item.u_type,
                        'addr': item.addr,
                        'tel': item.tel,
                        'email': item.email
                        }
                data_list.append(temp)
            if request.method == 'POST':
                print('sth post')
                method = request.POST.get('submit_method', None)
                print(method)
                if method == 'add':
                    # 添加数据
                    err_msg = add_user(request)
                elif method == 'change':
                    # 修改数据
                    u_id = get_post(request, 'u_id')
                    username = get_post(request, 'username')
                    password = get_post(request, 'password')
                    u_type = get_post(request, 'u_type')
                    if u_type == '':
                        u_type = '用户'
                    addr = get_post(request, 'addr')
                    if addr == '' or addr == 'None':
                        addr = None
                    tel = get_post(request, 'tel')
                    if tel == '' or tel == 'None':
                        tel = None
                    email = get_post(request, 'email')
                    if email == '' or tel == 'None':
                        email = None
                    c_password = models.User.objects.filter(u_id=u_id).first().password
                    if c_password != password:
                        password = check_psw.check(username, password)
                    models.User.objects.filter(u_id=u_id).update(username=username, password=password, u_type=u_type,
                                                                 addr=addr, tel=tel, email=email)
                    return redirect('/manage_user')
                elif method == 'del':
                    # 删除数据
                    u_id = request.POST.get('u_id', None)
                    models.User.objects.filter(u_id=u_id).delete()
                print(err_msg)
            return render(request, 'manage.html', {'data_list': data_list, 'page': '账户', 'table': table,
                                                   'username': username, 'usertype': 'World Maker', 'err_msg': err_msg})
        # 点击门店管理
        elif page == 'shop':
            table = {'s_id': '门店ID',
                     'name': '门店名',
                     'location': '门店地址',
                     'manager': '门店店长'}
            shop_list = models.Shop.objects.all()
            for item in shop_list:
                temp = {'s_id': item.s_id,
                        'name': item.name,
                        'location': item.location,
                        'manager': item.manager.u_id
                        }
                data_list.append(temp)
            if request.method == 'POST':
                print('sth post')
                method = request.POST.get('submit_method', None)
                print(method)
                if method == 'add':
                    # 添加数据
                    s_id = get_post(request, 's_id')
                    if s_id == '':
                        s_id = None
                    else:
                        temp = models.Shop.objects.filter(s_id=s_id)
                        if (len(temp)) > 0:
                            err_msg = '该门店已存在'
                    name = get_post(request, 'name')
                    location = get_post(request, 'location')
                    manager_id = get_post(request, 'manager')
                    manager = models.User.objects.filter(u_id=manager_id).first()
                    models.Shop.objects.create(s_id=s_id, name=name, location=location, manager=manager)
                    return redirect('/manage_shop')
                elif method == 'change':
                    # 修改数据
                    s_id = get_post(request, 's_id')
                    name = get_post(request, 'name')
                    location = get_post(request, 'location')
                    manager_id = get_post(request, 'manager')
                    manager = models.User.objects.filter(u_id=manager_id).first()
                    models.Shop.objects.filter(s_id=s_id).update(name=name, location=location, manager=manager)
                    return redirect('/manage_shop')
                elif method == 'del':
                    # 删除数据
                    s_id = request.POST.get('u_id', None)
                    models.Shop.objects.filter(s_id=s_id).delete()
                    return redirect('/manage_shop')
                print(err_msg)
            return render(request, 'manage.html', {'data_list': data_list, 'page': '门店', 'table': table,
                                                   'username': username, 'usertype': 'World Maker'})
        # 点击商品管理
        elif page == 'goods':
            table = {'g_id': '商品ID',
                     'name': '商品名',
                     'price': '商品价格'}
            goods_list = models.Goods.objects.all()
            for item in goods_list:
                temp = {'g_id': item.g_id,
                        'name': item.name,
                        'price': item.price,
                        }
                data_list.append(temp)
            if request.method == 'POST':
                print('sth post')
                method = request.POST.get('submit_method', None)
                print(method)
                if method == 'add':
                    # 添加数据
                    g_id = get_post(request, 'g_id')
                    if g_id == '':
                        g_id = None
                    else:
                        temp = models.Goods.objects.filter(g_id=g_id)
                        if (len(temp)) > 0:
                            err_msg = '该商品已存在'
                    name = get_post(request, 'name')
                    price = get_post(request, 'price')
                    models.Goods.objects.create(g_id=g_id, name=name, price=price)
                    return redirect('/manage_goods')
                elif method == 'change':
                    # 修改数据
                    g_id = get_post(request, 'g_id')
                    name = get_post(request, 'name')
                    price = get_post(request, 'price')
                    models.Goods.objects.filter(g_id=g_id).update(name=name, price=price)
                    return redirect('/manage_goods')
                elif method == 'del':
                    # 删除数据
                    g_id = request.POST.get('u_id', None)
                    models.Goods.objects.filter(g_id=g_id).delete()
                    return redirect('/manage_goods')
                print(err_msg)
            return render(request, 'manage.html', {'data_list': data_list, 'page': '商品', 'table': table,
                                                   'username': username, 'usertype': 'World Maker'})
        # 点击用户订单管理
        elif page == 'userOrder':
            table = {'id': '订单ID',
                     'goods_id': '商品ID',
                     'user_id': '用户ID',
                     'amount': '数量',
                     'time': '下单时间',
                     'price': '价格',
                     'status': '订单状态',
                     'method': '订单种类',
                     'remark': '备注'
                     }
            user_order_list = models.UserOrder.objects.all()
            for item in user_order_list:
                temp = {'id': item.id,
                        'goods_id': item.goods_id.g_id,
                        'user_id': item.user_id.u_id,
                        'amount': item.amount,
                        'time': item.time,
                        'price': item.price,
                        'status': item.status,
                        'method': item.method,
                        'remark': item.remark
                        }
                data_list.append(temp)
            if request.method == 'POST':
                print('sth post')
                method = request.POST.get('submit_method', None)
                print(method)
                if method == 'add':
                    # 添加数据
                    goods_id = get_post(request, 'goods_id')
                    goods_id = models.Goods.objects.filter(g_id=goods_id).first()
                    user_id = get_post(request, 'user_id')
                    user_id = models.User.objects.filter(u_id=user_id).first()
                    amount = get_post(request, 'amount')
                    price = get_post(request, 'price')
                    status = get_post(request, 'status')
                    method = get_post(request, 'method')
                    remark = get_post(request, 'remark')
                    models.UserOrder.objects.create(goods_id=goods_id, user_id=user_id, amount=amount,
                                                    price=price, status=status, method=method, remark=remark)
                    return redirect('/manage_userOrder')
                elif method == 'change':
                    # 修改数据
                    id_ = request.POST.get('id', None)
                    goods_id = get_post(request, 'goods_id')
                    goods_id = models.Goods.objects.filter(g_id=goods_id).first()
                    user_id = get_post(request, 'user_id')
                    user_id = models.User.objects.filter(u_id=user_id).first()
                    amount = get_post(request, 'amount')
                    price = get_post(request, 'price')
                    status = get_post(request, 'status')
                    method = get_post(request, 'method')
                    remark = get_post(request, 'remark')
                    models.UserOrder.objects.filter(id=id_).update(goods_id=goods_id, user_id=user_id, amount=amount,
                                                                   price=price, status=status, method=method,
                                                                   remark=remark)
                    return redirect('/manage_userOrder')
                elif method == 'del':
                    # 删除数据
                    id_ = request.POST.get('u_id', None)
                    models.UserOrder.objects.filter(id=id_).delete()
                    return redirect('/manage_userOrder')
                print(err_msg)
            return render(request, 'manage.html', {'data_list': data_list, 'page': '用户订单', 'table': table,
                                                   'username': username, 'usertype': 'World Maker'})
        # 点击门店订单管理
        elif page == 'shopOrder':
            table = {'id': '订单ID',
                     'goods_id': '商品ID',
                     'shop_id': '门店ID',
                     'amount': '数量',
                     'time': '下单时间',
                     'status': '订单状态'
                     }
            shop_order_list = models.ShopOrder.objects.all()
            for item in shop_order_list:
                temp = {'id': item.id,
                        'goods_id': item.goods_id.g_id,
                        'shop_id': item.shop_id.s_id,
                        'amount': item.amount,
                        'time': item.time,
                        'status': item.status
                        }
                data_list.append(temp)
            if request.method == 'POST':
                print('sth post')
                method = request.POST.get('submit_method', None)
                print(method)
                if method == 'add':
                    # 添加数据
                    goods_id = get_post(request, 'goods_id')
                    goods_id = models.Goods.objects.filter(g_id=goods_id).first()
                    shop_id = get_post(request, 'shop_id')
                    shop_id = models.Shop.objects.filter(s_id=shop_id).first()
                    amount = get_post(request, 'amount')
                    status = get_post(request, 'status')
                    models.ShopOrder.objects.create(goods_id=goods_id, shop_id=shop_id, amount=amount, status=status)
                    return redirect('/manage_shopOrder')
                elif method == 'change':
                    # 修改数据
                    id_ = request.POST.get('id', None)
                    goods_id = get_post(request, 'goods_id')
                    goods_id = models.Goods.objects.filter(g_id=goods_id).first()
                    shop_id = get_post(request, 'shop_id')
                    shop_id = models.Shop.objects.filter(s_id=shop_id).first()
                    amount = get_post(request, 'amount')
                    status = get_post(request, 'status')
                    models.ShopOrder.objects.filter(id=id_).update(goods_id=goods_id, shop_id=shop_id, amount=amount,
                                                                   status=status)
                    return redirect('/manage_shopOrder')
                elif method == 'del':
                    # 删除数据
                    id_ = request.POST.get('u_id', None)
                    models.ShopOrder.objects.filter(id=id_).delete()
                    return redirect('/manage_shopOrder')
                print(err_msg)
            return render(request, 'manage.html', {'data_list': data_list, 'page': '门店订单', 'table': table,
                                                   'username': username, 'usertype': 'World Maker'})
        # 点击门店库存
        elif page == 'shopStock':
            table = {'goods_id': '商品ID',
                     'shop_id': '门店ID',
                     'amount': '数量',
                     }
            shop_stock_list = models.ShopStock.objects.all()
            for item in shop_stock_list:
                temp = {'goods_id': item.goods_id.g_id,
                        'shop_id': item.shop_id.s_id,
                        'amount': item.amount
                        }
                data_list.append(temp)
            if request.method == 'POST':
                print('sth post')
                method = request.POST.get('submit_method', None)
                print(method)
                if method == 'add':
                    # 添加数据
                    goods_id = get_post(request, 'goods_id')
                    goods_id = models.Goods.objects.filter(g_id=goods_id).first()
                    shop_id = get_post(request, 'shop_id')
                    shop_id = models.Shop.objects.filter(s_id=shop_id).first()
                    amount = get_post(request, 'amount')
                    models.ShopStock.objects.create(goods_id=goods_id, shop_id=shop_id, amount=amount)
                    return redirect('/manage_shopStock')
                elif method == 'change':
                    # 修改数据
                    goods_id = get_post(request, 'goods_id')
                    goods_id = models.Goods.objects.filter(g_id=goods_id).first()
                    shop_id = get_post(request, 'shop_id')
                    shop_id = models.Shop.objects.filter(s_id=shop_id).first()
                    amount = get_post(request, 'amount')
                    models.ShopStock.objects.filter(goods_id=goods_id, shop_id=shop_id).update(amount=amount)
                    return redirect('/manage_shopStock')
                elif method == 'del':
                    # 删除数据
                    goods_id = request.POST.get('u_id', None)
                    shop_id = request.POST.get('u_id2', None)
                    models.ShopStock.objects.filter(goods_id=goods_id, shop_id=shop_id).delete()
                    return redirect('/manage_shopStock')
                print(err_msg)
            return render(request, 'manage.html', {'data_list': data_list, 'page': '门店库存', 'table': table,
                                                   'username': username, 'usertype': 'World Maker'})
        # 点击仓库库存
        elif page == 'warehouseStock':
            table = {'goods_id': '商品ID',
                     'amount': '数量',
                     }
            warehouse_stock_list = models.WarehouseStock.objects.all()
            for item in warehouse_stock_list:
                temp = {'goods_id': item.goods_id.g_id,
                        'amount': item.amount
                        }
                data_list.append(temp)
            if request.method == 'POST':
                print('sth post')
                method = request.POST.get('submit_method', None)
                print(method)
                if method == 'add':
                    # 添加数据
                    goods_id = get_post(request, 'goods_id')
                    goods_id = models.Goods.objects.filter(g_id=goods_id).first()
                    amount = get_post(request, 'amount')
                    models.WarehouseStock.objects.create(goods_id=goods_id, amount=amount)
                    return redirect('/manage_warehouseStock')
                elif method == 'change':
                    # 修改数据
                    goods_id = get_post(request, 'goods_id')
                    goods_id = models.Goods.objects.filter(g_id=goods_id).first()
                    amount = get_post(request, 'amount')
                    models.WarehouseStock.objects.filter(goods_id=goods_id).update(amount=amount)
                    return redirect('/manage_warehouseStock')
                elif method == 'del':
                    # 删除数据
                    goods_id = request.POST.get('u_id', None)
                    models.WarehouseStock.objects.filter(goods_id=goods_id).delete()
                    return redirect('/manage_warehouseStock')
                print(err_msg)
            return render(request, 'manage.html', {'data_list': data_list, 'page': '仓库库存', 'table': table,
                                                   'username': username, 'usertype': 'World Maker'})


# 获取post请求内容（可无视）
def get_post(request, name):
    res = request.POST.get(name, None)
    return res


# 后台管理添加用户
def add_user(request):
    u_id = get_post(request, 'u_id')
    if u_id == '':
        u_id = None
    else:
        temp = models.User.objects.filter(u_id=u_id)
        if (len(temp)) > 0:
            err_msg = '该用户已存在'
            return err_msg
    username = get_post(request, 'username')
    password = get_post(request, 'password')
    u_type = get_post(request, 'u_type')
    if u_type == '':
        u_type = '用户'
    addr = get_post(request, 'addr')
    if addr == '':
        addr = None
    tel = get_post(request, 'tel')
    if tel == '':
        tel = None
    email = get_post(request, 'email')
    if email == '':
        email = None
    password = check_psw.check(username, password)
    models.User.objects.create(u_id=u_id, username=username, password=password, u_type=u_type, addr=addr,
                               tel=tel, email=email)
    return redirect('/manage_user')


# 用于将string类型转换成bytes类型
def s_to_b(string):
    b = eval(string)
    res = b.decode('utf-8')
    return res


# 当用户类型无法识别时用于返回错误页面
def no_type(request):
    return render(request, 'no_type.html')


# 商品库存不足时返回错误页面
def not_enough(request):
    return render(request, 'not_enough.html')


# 商品库存不足时返回错误页面
def not_enough_w(request):
    return render(request, 'not_enough_w.html')


# 当用户类型无权访问当前页面时返回错误页面
def no_right(request):
    return render(request, '403.html')


# 404
def page_not_found(request, *args):
    return render(request, '404.html')


# 数据库初始化
def default_database(request):
    # models.User.objects.create(u_id=1, username='superuser', password='123', u_type='超级管理员')
    # models.User.objects.create(u_id=2, username='customer', password='123', u_type='用户')
    #
    # models.Goods.objects.create(g_id=1, name='apple', price=3)
    # models.Goods.objects.create(g_id=2, name='pear', price=4)
    # models.Goods.objects.create(g_id=3, name='banana', price=2)

    # models.Shop.objects.create(s_id=1, name='BUPT', location='Rd.xitucheng No.10 haidian beijing China')

    apple = models.Goods.objects.filter(g_id=1).first()
    pear = models.Goods.objects.filter(g_id=2).first()
    banana = models.Goods.objects.filter(g_id=3).first()
    u = models.User.objects.filter(u_id=2).first()
    bupt = models.Shop.objects.filter(s_id=1).first()
    # models.UserOrder.objects.create(goods_id=apple, user_id=u, amount=1, price=3, status='付款成功，等待发货')
    # models.UserOrder.objects.create(goods_id=pear, user_id=u, amount=2, price=8, status='发货完成，等待取货')
    # models.UserOrder.objects.create(goods_id=banana, user_id=u, amount=1, price=2, status='等待付款')

    # models.ShopOrder.objects.create(goods_id=apple, shop_id=bupt, amount=100, status='等待发货')
    # models.ShopOrder.objects.create(goods_id=pear, shop_id=bupt, amount=200, status='运送中')
    # models.ShopOrder.objects.create(goods_id=banana, shop_id=bupt, amount=100, status='已收货')

    # models.ShopStock.objects.create(goods_id=apple, shop_id=bupt, amount=10)
    # models.ShopStock.objects.create(goods_id=pear, shop_id=bupt, amount=30)
    # models.ShopStock.objects.create(goods_id=banana, shop_id=bupt, amount=120)
    #
    # models.WarehouseStock.objects.create(goods_id=apple, amount=300)
    # models.WarehouseStock.objects.create(goods_id=pear, amount=350)
    # models.WarehouseStock.objects.create(goods_id=banana, amount=200)

    # models.Replenish.objects.create(goods_id=apple, amount=100, price=200)

    # models.Tally.objects.create(t_type='进货', goods_id=apple, amount=10, order_id=1, price=-200)
    # models.Tally.objects.create(t_type='线上购买', goods_id=apple, amount=1, order_id=1, price=3)
    # models.Tally.objects.create(t_type='线上购买', goods_id=pear, amount=2, order_id=2, price=8)
    # models.Tally.objects.create(t_type='线下自提', goods_id=banana, amount=1, order_id=3, price=2)

    # 自动添加商品
    # f = open('/Users/teihiroshibon/PycharmProjects/YZJ/static/img/products/fruit.jpg', 'rb')
    # temp = f.read()
    # f.close()
    # for i in range(100):
    #     i_s = str(i)
    #     f2 = open('/Users/teihiroshibon/PycharmProjects/YZJ/static/img/products/fruit' + i_s + '.jpg', 'wb')
    #     f2.write(temp)
    #     f2.close()
    #     models.Goods.objects.create(name='fruit' + i_s, price=1)

    return HttpResponse('done')


# 库存同步
def check_stock(request):
    # goods_list = models.Goods.objects.all()
    # for goods in goods_list:
    #     仓库库存同步
    #     stock = models.WarehouseStock.objects.filter(goods_id=goods).first()
    #     if stock is None:
    #         models.WarehouseStock.objects.create(goods_id=goods, amount=0)
    #     门店库存同步
    #     shop_list = models.Shop.objects.all()
    #     for shop in shop_list:
    #         stock = models.ShopStock.objects.filter(goods_id=goods, shop_id=shop).first()
    #         if stock is None:
    #             models.ShopStock.objects.create(goods_id=goods, shop_id=shop, amount=0)
    return HttpResponse('done')
