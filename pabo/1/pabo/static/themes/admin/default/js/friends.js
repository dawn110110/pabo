$(function(){
    var _required = {required: true};
    // 修改友链
    $('[id^="form-mod"]').each(function(i, v){
        form_validate(v, {name: _required, link: _required}, function($form){
            var $btn = $(':submit', $form);
            if(is_submiting($btn)){
                return false;
            }
            block_submit($btn);
            $.post($form.attr('action'), $form.serialize(), function(jsn){
                unblock_submit($btn);
                notify(jsn.err ? jsn.msg : '修改成功');

                var link = $('[name="link"]', $form).val();
                var name = $('[name="name"]', $form).val();
                $('h5', $form.parents('.widget-box:first'))
                .attr('data-original-title', '前往 ' + link)
                .find('a').attr('href', link).find('span').text(name);
                $('[name="raw"]', $form).val(link);

                var $iframe = $form.next();
                if(link != $iframe.attr('src')){
                    $iframe.attr('src', link);
                }
            });
        });
    });


    // 删除友链
    $(document).on('click', 'a.del', function(){
        var self = $(this);
        var raw = self.siblings('[name="raw"]').val();
        if(is_submiting(self)){
            return false;
        }
        if(confirm('确认删除友链[ ' + raw + ' ]吗?')){
            block_submit(self);
            $.post('/admin.del.link.json', {raw: raw}, function(jsn){
                var msg;
                if(!jsn.err){
                    msg = '友链[ ' + raw + ' ]已删除';
                    self.parents('.row-fluid:first').remove();
                }else{
                    msg = jsn.msg;
                }
                notify(msg);
                unblock_submit(self);
            });
        }
    });

    // 添加友链
    form_validate('#form-add', {name: _required, link: _required}, function($form){
        var $btn = $(':submit', $form);
        if(is_submiting($btn)){
            return false;
        }
        block_submit($btn);
        $.post($form.attr('action'), $form.serialize(), function(jsn){
            var msg;
            if(!jsn.err){
                msg = '添加成功';
                location.reload();
            }else{
                msg = jsn.msg;
            }
            notify(msg);
            unblock_submit($btn);
        });
    });
});
