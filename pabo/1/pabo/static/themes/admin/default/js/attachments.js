$(function(){
    function get_img_key($li){
        return $('a', $li).attr('href').split('/')[2];
    }
    // 显示更多
    $('.view-more').click(function(){
        var self = $(this);
        var $ul = self.prev();
        var marker = get_img_key($('li:last', $ul));
        $.get('/admin.get.imgs.marker.' + marker, function(html){
            if(html.length == 0){
                self.hide();
                notify('没有更多的图片可以加载了');
            }else{
                var $last_li = $('li:last', $ul);
                $ul.append(html);
                init_copy_url_event($last_li.nextAll());
                notify('加载完成');
            }
        });
    });


    // 删除图片
    $(document).on('click', 'a.del', function(){
        if(confirm('确认删除吗?')){
            var self = $(this);
            var $a = self.siblings('.thumbnail');
            var $li, key;
            if($a.length == 1){
                // 如果点击的是是搜索那里的删除
                key = $a.attr('href').split('/')[2].split('?')[0];
            }else{
                $li = self.parents('li:first');
                key = get_img_key($li);
            }
            $.post('/admin.del.img', {key: key}, function(){
                notify('图片:<br>' + key + '<br>已删除', '/img/160x120/' + key);
                if($a.length == 1){
                    $a.parents('.center:first').hide();
                }else{
                    $li.remove();
                    if($('ul.thumbnails').find('li').length == 0){
                        location.reload();
                    }
                }
            });
        }
    });


    // 复制图片网址
    ZeroClipboard.setDefaults({
        moviePath: $('.container-fluid').data('swf'),
        hoverClass: 'clip-hover',
        useNoCache: false
    });
    function init_copy_url_event($lis){
        var clip = new ZeroClipboard($('.copy', $lis));
        clip.addEventListener('mouseDown', function(){
            clip.setText(get_img_key($(this).parents('li:first')));
        });
        clip.addEventListener('complete', function(client, args){
            notify('图片网址已复制到剪贴板', '/img/160x120/' + args.text);
        });
    }
    init_copy_url_event($('.thumbnails li'));


    // 搜索图片
    (function(){
        var $search_input = $('input[name="name"]');
        var $search_result = $('#img-search-result');
        var $a = $('a.thumbnail', $search_result);
        var $img = $('img', $a);
        $('#img-search').click(function(){
            $search_result.show();
            var key = $search_input.val() + '?v=' + Math.random();
            $img.attr('src', '/img/160x120/' + key);
            $a.attr('href', '/img/' + key);
            $search_input.focus().select();
        });
    })();
});
