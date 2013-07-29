$(function(){
    $('#content').on('click', '.del', function(){
        // 删除文章
        var $btn = $(this);
        var $article = $btn.parents('.article:first');
        var title = $('h5', $article).attr('title');
        if(confirm('确认删除文章《' + title + '》吗?')){
            if(is_submiting($btn)){
                return false;
            }
            block_submit($btn);
            var id = $article.data('id');
            $.post('/admin.del.article.json', {id: id}, function(jsn){
                var msg;
                if(jsn.err){
                    msg = jsn.msg;
                }else{
                    msg = '文章:<br>' + title + '<br> 已删除';
                    $article.remove();
                    if($('.article').length == 0){
                        location.reload();
                    }
                }
                unblock_submit($btn);
                return notify(msg);
            });
        }
    }).on('click', '.pagination li:not(.disabled, .active)', function(){
        // 分页获取
        var $li = $(this);
        var page_num;
        if($li.hasClass('prev')){
            page_num = $li.siblings('.active').text() * 1 - 1;
        }else if($li.hasClass('next')){
            page_num = $li.siblings('.active').text() * 1 + 1;
        }else{
            page_num = $li.text();
        }
        $('#articles').load('/admin.get.articles.page.' + page_num);
    });


    // 监听文章变化
    window.onstorage = function(e){
        switch(e.key){
            case consts.K_ARTICLE_REFRESH:
                storage.removeItem(e.key);
                var id = e.newValue;
                $('.article[data-id="' + id + '"]').load('/admin.get.article.box.' + id);
        }
    };
});
