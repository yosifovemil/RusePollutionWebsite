$(document).ready(function(){
    $('.tooltip_max').click(function(){
      var el = $('.tooltip_max').find('.tooltiptext');
      el.css('visibility') == 'visible' ?
        el.css('visibility','hidden') :
        el.css('visibility','visible');
    });
});

$(document).ready(function(){
    $('.tooltip_mean').click(function(){
      var el = $('.tooltip_mean').find('.tooltiptext');
      el.css('visibility') == 'visible' ?
        el.css('visibility','hidden') :
        el.css('visibility','visible');
    });
});