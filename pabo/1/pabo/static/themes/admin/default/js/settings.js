$(function(){
    $('select').select2({width: 290});

    // 修改admin信息
    form_validate('#form-admin-info-mod', {
        name: {required: true},
        pwd: {required: true, minlength: 6, maxlength: 20},
        confirm: {required: true, minlength: 6, maxlength: 20, equalTo: '[name="pwd"]'},
        email: {required: true, email: true}
    }, function($form){
        var $btn = $(':submit', $form);
        if(is_submiting($btn)){
            return false;
        }
        block_submit($btn);
        $.post($form.attr('action'), $form.serialize(), function(jsn){
            var msg;
            if(!jsn.err){
                $('[name="pwd"], [name="confirm"]', $form).val('');
                msg = '管理员信息修改成功';
            }else{
                msg = jsn.msg;
            }
            unblock_submit($btn);
            notify(msg);
        });
    });

    // 修改站点信息
    _required = {required: true};
    form_validate('#form-site-info-mod', {
        login_url: _required,
        title: _required,
        author: _required,
        app: {number: true, required: true, min: 5, max: 20}
    }, function($form){
        var $btn = $(':submit', $form);
        if(is_submiting($btn)){
            return false;
        }
        block_submit($btn);
        $.post($form.attr('action'), $form.serialize(), function(jsn){
            var msg;
            if(!jsn.err){
                $('[name="pwd"], [name="confirm"]', $form).val('');
                msg = '管理员信息修改成功';
            }else{
                msg = jsn.msg;
            }
            unblock_submit($btn);
            notify(msg);
        });
    });
});
