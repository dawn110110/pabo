$(function(){
    // 修改文章页面
    try{
        $('select').select2({width: 150});

        // 监听分类列表变化
        window.onstorage = function(e){
            switch(e.key){
                case consts.K_CLASSES_REFRESH:
                    storage.removeItem(e.key);
                    $('select[name="cls"]').load('/admin.get.select.classes.json');
            }
        };

        var $form = $('form');

        // 保存
        var _required = {required: true};
        form_validate($form, {
            cls: _required,
            title: _required,
            md: _required
        }, function($form){
            var $btn = $(':submit', $form);
            if(is_submiting($btn)){
                return false;
            }
            var md = $('#textarea').val();
            if(md.indexOf('<!--more-->') == -1){
                if(!confirm('没有在文章内容中检测到<!--more-->标签，文章将以全文做为摘要，确认发表吗？')){
                    return;
                    }
            }
            block_submit($btn);
            $('[name="md"]', $form).val(md);
            $.post($form.attr('action'), $form.serialize(), function(jsn){
                var msg;
                if(jsn.err){
                    msg = jsn.msg;
                }else{
                    msg = '保存成功';
                    // 通知其他页面更新文章
                    storage[consts.K_ARTICLE_REFRESH] = $('input[name="id"]').val();
                }
                unblock_submit($btn);
                return notify(msg);
            });
        });
    }catch(e){}


    // 编辑器
    var $preview = $('#preview');
    var $editor = $('#editor');
    var $textarea = $('textarea', $editor);

    // marked设置
    marked.setOptions({
        gfm: true,
        tables: true,
        breaks: false,
        pedantic: true,
        sanitize: false,
        smartLists: false,
        highlight: function(code, lang){
            setTimer('prettify', function(){
                $('pre code', $preview).addClass('prettyprint');
                prettyPrint();
            }, 50);
            // 将\n修改为<br>，因为在ie里面pre标签中的\n不会产生换行
            return code.replace(/>/g, '&gt;').replace(/</g, '&lt;').
                        replace(/\n/g, '<br>');
        }
    });

    // 动态改变输入框的大小
    $(window).on('resize', function(){
        setTimer('resize', function(){
            $textarea.height($editor.height() - 32);
        }, 100);
    }).resize();

    $textarea.on('input', function(){
        setTimer('input', function(){
            $preview.html(marked($textarea.val()));
            $('p:has(img)').add($('embed, iframe').wrap('<p></p>').parent())
            .css('text-align', 'center');
        }, 10);
    }).focus(function(){
        $textarea.trigger('input');
    }).on('keydown', function(e){
        var k = e.which;
        // TAB键
        if(k == 9){
            var start = this.selectionStart;
            var end = this.selectionEnd;
            var self = $(this);
            var val = self.val();
            self.val(val.substring(0, start) + '    ' + val.substring(end));
            this.selectionStart = this.selectionEnd = start + 4;
            return false;
        }
    }).trigger('input').css('overflow', 'auto').focus();
});


/* 设置定时器
 * >>> setTimer('scroll_timer', function(){}, 1000);
 * name: 定时器的名字[名字将绑定在window对象上，请确保每个定时器名字唯一]
 * callback: 回调函数
 * time: 延迟时间[单位毫秒]
 */
function setTimer(name, callback, delay){
    // 加个后缀，避免与其他window上的属性冲突
    var name = name + '_timer_pabo_';
    if(window[name]){
        clearTimeout(window[name]);
    }
    window[name] = setTimeout(callback, delay);
}
