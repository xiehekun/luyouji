$.ajaxSetup({
    error : function(xhr, textStatus, error) {
        var err_code = xhr.status;
        switch (err_code) {
        case 404:
            alert('请求路径没有找到.');
            break;
        case 500:
            alert('服务器发生错误, 请稍后再试.');
            break;
        case 405:
            alert('缺少必须的请求参数.');
            break;
        case 403:
            alert('请先登陆.');
            break;
        default:
            alert('请求发生错误.');
            break;
        }
    },
    beforeSend : function(xhr) {
        if (!(document.cookie || navigator.cookieEnabled)) {
            alert('您的浏览器关闭了cookie功能, 这样可能会影响您在本站的体验.');
        }
    }
});

//计算两个日期之间相差的天数
function daysBetween(DateOne, DateTwo) {
    var OneMonth = DateOne.substring(5, DateOne.lastIndexOf('-'));
    var OneDay = DateOne
            .substring(DateOne.length, DateOne.lastIndexOf('-') + 1);
    var OneYear = DateOne.substring(0, DateOne.indexOf('-'));

    var TwoMonth = DateTwo.substring(5, DateTwo.lastIndexOf('-'));
    var TwoDay = DateTwo
            .substring(DateTwo.length, DateTwo.lastIndexOf('-') + 1);
    var TwoYear = DateTwo.substring(0, DateTwo.indexOf('-'));

    var cha = ((Date.parse(OneMonth + '/' + OneDay + '/' + OneYear) - Date
            .parse(TwoMonth + '/' + TwoDay + '/' + TwoYear)) / 86400000);
    return Math.abs(cha);
}

//格式化时间
Date.prototype.Format = function(formatStr) {
    var str = formatStr;
    var Week = [ '日', '一', '二', '三', '四', '五', '六' ];

    str = str.replace(/yyyy|YYYY/, this.getFullYear());
    str = str.replace(/yy|YY/,
            (this.getYear() % 100) > 9 ? (this.getYear() % 100).toString()
                    : '0' + (this.getYear() % 100));
    str = str.replace(/MM/, (this.getMonth() + 1) > 9 ? (this.getMonth() + 1) + ""
            : '0' + (this.getMonth() + 1));
    str = str.replace(/M/g, this.getMonth() + 1);

    str = str.replace(/w|W/g, Week[this.getDay()]);

    str = str.replace(/dd|DD/, this.getDate() > 9 ? this.getDate().toString()
            : '0' + this.getDate());
    str = str.replace(/d|D/g, this.getDate());

    str = str.replace(/hh|HH/, this.getHours() > 9 ? this.getHours().toString()
            : '0' + this.getHours());
    str = str.replace(/h|H/g, this.getHours());
    str = str.replace(/mm/, this.getMinutes() > 9 ? this.getMinutes()
            .toString() : '0' + this.getMinutes());
    str = str.replace(/m/g, this.getMinutes());

    str = str.replace(/ss|SS/, this.getSeconds() > 9 ? this.getSeconds()
            .toString() : '0' + this.getSeconds());
    str = str.replace(/s|S/g, this.getSeconds());

    return str;
};


$.fn.autoTextarea = function (options) {
    var defaults = {
        maxHeight: null,//文本框是否自动撑高，默认：null，不自动撑高；如果自动撑高必须输入数值，该值作为文本框自动撑高的最大高度
        minHeight: $(this).height() //默认最小高度，也就是文本框最初的高度，当内容高度小于这个高度的时候，文本以这个高度显示
    };
    var opts = $.extend({}, defaults, options);
    return $(this).each(function () {
        $(this).bind("paste cut keydown keyup focus blur", function () {
            var height, style = this.style;
            this.style.height = opts.minHeight + 'px';
            if (this.scrollHeight > opts.minHeight) {
                if (opts.maxHeight && this.scrollHeight > opts.maxHeight) {
                    height = opts.maxHeight;
                    style.overflowY = 'scroll';
                } else {
                    height = this.scrollHeight;
                    style.overflowY = 'hidden';
                }
                style.height = height + 'px';
            }
        });
    });
};
