
$(function () {
// 后台管理页面
    // 修改用户列表的操作
    // 点击修改时获取表格内所有数据，并写入模态框
    $('.u_change').click(function () {
        var tar = $('#u_change_form').children().first().children().children().last();     // 获取模态框中最后一个input标签
        $(this).parent().parent().parent().prevAll().each(function(){
            tar.val($(this).text());
            tar = tar.parent().prev().children();
        });
        // 在修改模态框中显示当前用户ID
        var u_id_t = $('#u_idcid').val();
        u_id.prev().text(u_id_l + u_id_t);
        // 在修改模态框中显示当前门店ID
        var s_id_t = $('#s_idcid').val();
        s_id.prev().text(s_id_l + s_id_t);
        // 在修改模态框中显示当前商品ID
        var g_id_t = $('#g_idcid').val();
        g_id.prev().text(g_id_l + g_id_t);
        // 在修改模态框中显示当前ID
        var id_t = $('#idcid').val();
        g_id.prev().text(id_l + id_t);
    });
    // 点击删除时获取id
    $('.u_del').click(function () {
       var a = $(this).parent().parent().parent().prevAll().last().text();
       console.log(a);
       $('#u_iddid').val(a);
       var b = $(this).parent().parent().parent().prevAll().last().next().text();
       console.log(a);
       $('#u_iddid2').val(b);
    });
    // 修改时不显示u_id
    var u_id = $('#u_idcid').addClass('hide');
    u_id_l = u_id.prev().text();
    // 修改时不显示s_id
    var s_id = $('#s_idcid').addClass('hide');
    s_id_l = s_id.prev().text();
    // 修改时不显示g_id
    var g_id = $('#g_idcid').addClass('hide');
    g_id_l = g_id.prev().text();
    // 修改数据时隐藏id
    var id = $('#idcid').addClass('hide');
    id_l = id.prev().text();
    // 添加用户时用户类型默认填入'用户'
    $('#u_typeaid').attr('value', '用户');
    // 添加数据时隐藏id
    $('#idaid').parent().addClass('hide');
    // 添加数据时隐藏时间
    $('#timeaid').parent().addClass('hide');
    // 修改数据时隐藏时间
    $('#timecid').parent().addClass('hide');

// 登录页面
    // 注册按钮
    $('#u_signup').click(function () {
        window.location.replace("/register.html");
    });
    // 清除错误信息
    setInterval(function () {
        $('.err_msg').text('')
    }, 2000);
    // 占位
    $('.err_msg').css('height', '25px');
// 注册页面
    // 登录按钮
    $('#u_login').click(function () {
        window.location.replace("/login.html");
    });
// 用户个人中心页面
    // 取消按钮
    $('#u_cancel').click(function () {
        $(':text').val('');
    });
// 购买页面
    // 点击购买按钮后获取数据填入模态框中
    $('.u_buy_button').click(function() {
        var tar = $(this).parent().parent().next();
        var goods_name = tar.children().first().children().text();
        var goods_price = tar.children().last().text();
        $('#goodsname').val(goods_name);
        $('#price').val(goods_price);
    // 生成定时器计算总价
        var c_obj = setInterval(function () {
            var account = $('#account').val();
            var rep = /^\d+$/;
            if (rep.test(account)) {
                goods_price = tar.children().last().text();
                rep = /\d+/;
                goods_price = rep.exec(goods_price);
                var t_price = account * goods_price;
                var res = '总价：' + t_price.toString();
                $('#u_price').text(res);
            }
            // 判断是否可选门店
            var method = $('#u_method').val();
            if (method === '0'){
                $('#u_shop').attr('disabled',false);
            }else if(method === '1'){
                $('#u_shop').attr('disabled',true);
            }
            // 当模态框不显示时清空定时器
            if($('#u_goodsdetail').hasClass('show')){
                }else {
                    clearInterval(c_obj);
                }
        }, 1000)
    });
    // 用户确认收货
    $('.u_getconfirm_u').click(function () {
        var id = $(this).parent().prevAll().last().text();
        $('#u_userorder_u').val(id);
    });
// 门店店长管理页面
    // 确认取货模态框
    $('.u_getconfirm_b').click(function () {
        var id = $(this).parent().prevAll().last().text();
        $('#u_userorder').val(id)
    });
    $('.u_getconfirm_ss').click(function () {
        var id = $(this).parent().prevAll().last().text();
        $('#u_shoporder').val(id);
    });
    // 库存管理
    // 修改库存
    $('.u_changestock').click(function () {
        var name = $(this).parent().prevAll().last().text();
        var amount = $(this).parent().prevAll().first().text();
        $('#u_goods_id_c').val(name);
        $('#amount_c').val(amount);
    });
    // 进货申请
    $('.u_addstock').click(function () {
        var name = $(this).parent().prevAll().last().text();
        $('#u_goods_id_a').val(name)
    });
// 仓库管理页面
    // 确认发货
    $('.u_getconfirm_ws').click(function () {
        var id = $(this).parent().prevAll().last().text();
        console.log(id);
        $('#u_shoporder_w').val(id);
    });
    // 库存管理
    // 修改库存
    $('.u_changestock_w').click(function () {
        var name = $(this).parent().prevAll().last().text();
        var amount = $(this).parent().prevAll().first().text();
        console.log(name);
        console.log(amount);
        $('#u_goods_id_wc').val(name);
        $('#amount_wc').val(amount);
    });
    // 进货申请
    $('.u_addstock_w').click(function () {
        var name = $(this).parent().prevAll().last().text();
        console.log(name);
        $('#u_goods_id_wa').val(name)
    });
// 电商管理界面
    // 确认发货模态框
    $('.u_getconfirm_o').click(function () {
        var id = $(this).parent().prevAll().last().text();
        console.log(id);
        $('#u_userorder_o').val(id);
    });

});


