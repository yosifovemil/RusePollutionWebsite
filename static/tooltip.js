$(document).ready(function(){
    $('.tooltip').click(function(){
      var el = $('.tooltiptext');
      el.css('visibility') == 'visible' ?
        el.css('visibility','hidden') :
        el.css('visibility','visible');
    });
});