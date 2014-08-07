var del_pd_img = function(obj, _id, dd_id, img){
    $.get('/plan/day_img?_id=' + _id + "&dd_id=" + dd_id + "&img_url=" + encodeURI(img), function(resp){
        var data = eval('(' + resp + ')');
        if(data['succ']) {
            $(obj).parents('tr').remove();
        }
    });
};
$(function() {
    $('#fileupload').fileupload({
        autoUpload : false,// 是否自动上传
        dataType : 'json',
        maxFileSize : 4 * 1024 * 1024,
        acceptFileTypes : /(\.|\/)(gif|jpe?g|png)/i,
        maxNumberOfFiles : 5,
        messages: {
            maxNumberOfFiles: '最多一次上传5张图片',
            acceptFileTypes: '错误的图片类型',
            maxFileSize: '图片大小超过4M'
        },
        done : function(e, data) {// 设置文件上传完毕事件的回调函数
            var res = data.result;
            var progress = data.context.find('.progress');
            progress.removeClass('active').addClass('fade').hide()
            if(res['succ']) {
                var ht = '<span style="color:green;">上传成功</span>&nbsp;&nbsp;<a style="color:gray;" href="javascript:void(0);" onclick="del_pd_img(this, \'' + res['_id'] +'\', \'' + res['dd_id'] + '\', \'' + res['img_url'] + '\');">删除</a>'
                progress.after(ht);
            } else {
                var code = res['code'];
                var ht = "";
                switch(code) {
                case 1:
                    ht = '<span style="color:red;">系统错误</span>';
                    break;
                case 2:
                    ht = '<span style="color:red;">文件未找到</span>';
                    break;
                case 3:
                    ht = '<span style="color:red;">错误的图片类型</span>';
                    break;
                case 4:
                    ht = '<span style="color:red;">图片大小超过4M</span>';
                    break;
                case 5:
                    ht = '<span style="color:red;">上传失败</span>';
                    break;
                }
            }
        }
    });
});
