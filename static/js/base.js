$(document).ready(function(){
    url = window.location.href;
    //$('#topTab').children().removeClass('active');
    lasturl = url.split('/');
    classname = '/' + lasturl[lasturl.length-1]; 
    if (classname == '/classroom'){
        $('#top1').addClass('active');
        console.debug(classname);
    }
    if (classname == '/curriculum'){
        $('#top2').addClass('active');
        console.debug(classname);
    }
    if (classname == '/about'){
        $('#top3').addClass('active');
        console.debug(classname);
    }
});
