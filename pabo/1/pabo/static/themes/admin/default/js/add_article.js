$(function(){
    $('select').select2({width: 170});

    // 上传图片
    var $dropbox = $('#dropbox'),
        $message = $('.message', $dropbox);
    var maxfiles = 99,
        maxfilesize = 4;
    var t = 0;
    ZeroClipboard.setDefaults({moviePath: $dropbox.data('swf')});
    $dropbox.filedrop({
        paramname: 'pic',
        maxfiles: maxfiles,
        maxfilesize: maxfilesize,
        rename: function(name){
            ++t;
            var ext = '.' + name.match(/.*\.(jpg|gif|bmp|png)$/)[1];
            return t + ext;
        },
        url: '/admin.upload.img.json',
        uploadFinished: function(i, file, jsn){
            if(jsn.err){
                notify(jsn.msg);
            }else{
                var $preview = $.data(file).addClass('done');
                var $progress = $('.progress', $preview).text('复制网址').data('url', jsn.url);
                var clip = new ZeroClipboard($progress);
                clip.addEventListener('mouseDown', function(client){
                    clip.setText($(this).data('url'));
                });
                clip.addEventListener('complete', function(client, args){
                    notify('图片网址:<br>' + args.text + '<br>已复制到剪贴板');
                });
            }
        },
        error: function(err, file){
            switch(err){
                case 'BrowserNotSupported':
                    notify('你的浏览器不支持HTML5拖放上传,请使用Google Chrome浏览器.');
                    break;
                case 'TooManyFiles':
                    notify('请最多上传' + maxfiles + '张图片');
                    break;
                case 'FileTooLarge':
                    notify(file.name + '的大小超过了' + maxfilesize + 'M');
                    break;
                default:
                    break;
            }
        },
        beforeEach: function(file){
            if(!file.type.match(/^image\/(png|jpeg|gif|bmp)/)){
                return notify('只能上传png、gif、bmp以及jpg格式的图片');
            }
        },
        uploadStarted: function(i, file, len){
            var tpl = '<div class="preview">'+
                        '<span class="image-holder">'+
                            '<img><span class="uploaded"></span>'+
                        '</span>'+
                        '<div class="progress-holder">'+
                            '<div class="progress"></div>'+
                        '</div>'+
                      '</div>';
            var $preview = $(tpl),
                $image = $('img', $preview);

            var reader = new FileReader();

            $image.width = 100;
            $image.height = 100;

            reader.onload = function(e){
                $image.attr('src', e.target.result);
            };

            reader.readAsDataURL(file);

            $message.hide();
            $preview.appendTo($dropbox);

            $.data(file, $preview);
        }
    });


    // 发表文章
    var $form = $('#article-form');
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
        if($('textarea', $form).val().indexOf('<!--more-->') == -1){
            if(!confirm('没有在文章内容中检测到<!--more-->标签，文章将以全文做为摘要，确认发表吗？')){
                return;
                }
        }
        block_submit($btn);
        $.post($form.attr('action'), $form.serialize(), function(jsn){
            var msg;
            if(jsn.err){
                msg = jsn.msg;
            }else{
                msg = '发表成功';
                $('[name="title"], [name="md"]', $form).val('');
                $('[name="title"]').focus();
            }
            unblock_submit($btn);
            notify(msg);
        });
    });


    // 监听分类列表变化
    window.onstorage = function(e){
        var k = e.key;
        switch(k){
            case consts.K_CLASSES_REFRESH:
                $('select[name="cls"]').load('/admin.get.select.classes.json');
                storage.removeItem(k);
        }
    };
});
