$(document).ready(function(){
    url = window.location.href;
    lasturl = url.split('/');
    classname = '/' + lasturl[lasturl.length-1]; 
    load_table();
    function load_table(){
        console.debug("hello");
        $.ajax({
            type: 'POST',
            url: '/github',
            data: {"site": "Tornado-data"},
            dataType: "json",
            success: function(data){
                console.debug("hello");
                var github_table  = "<table class='table table-striped'><tr>";
                for (var i in data){
                    github_table += "<td class='solid'>#" + i + "</td>";
                    github_table += "<td class='solid'>" + "<a href='https://github.com/" + data[i]["login"] + "' target='_blank'>" + data[i]["login"] + "</a>" + "&nbsp(" + data[i]["name"] + ")" + "</td>";
                    github_table += "<td class='solid'>" + data[i]["language"] + "</td>";
                    github_table += "<td class='solid'>" + data[i]["location"] + "</td>";
                    github_table += "<td class='solid'>" + "<img height='48' width='48' src=" + data[i]["gravatar"] + "/>" + "</td>";
                    github_table +="</tr><tr>";
                }
                github_table += "</tr><table>";
                $("#github-table").html(github_table);
            } 
        });
    }
});
