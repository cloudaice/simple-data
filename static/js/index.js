$(document).ready(function(){
    $("#myTab a").click(function(e){
        e.preventDefault();
        $(this).tab("show");
    })

    function load_table(url){
        $.ajax({
            type: 'POST',
            url: url,
            data: {"site": "Tornado-data"},
            dataType: "json",
            success: function(data){
                var github_table  = "<table class='table table-striped'><thead><tr>";
                github_table +=  "<th>Rank</th>";
                github_table +=  "<th>Name</th>";
                github_table +=  "<th>Score</th>";
                github_table +=  "<th>Language</th>";
                github_table +=  "<th>Location</th>";
                github_table +=  "<th>Profile</th>";
                github_table += "</tr></thead><tr>";
                for (var i in data){
                    var count = parseInt(i) + 1;
                    github_table += "<td class='solid'>#" + count + "</td>";
                    github_table += "<td class='solid'>" + "<a href='https://github.com/" + data[i]["login"] + "' target='_blank'>" + data[i]["login"] + "</a>" + "&nbsp(" + data[i]["name"] + ")" + "</td>";
                    github_table += "<td class='solid'>" + parseInt(data[i]["score"]) + "</td>";
                    github_table += "<td class='solid'>" + data[i]["language"] + "</td>";
                    github_table += "<td class='solid'>" + data[i]["location"] + "</td>";
                    github_table += "<td class='solid'>" + "<img height='48' width='48' src=" + data[i]["gravatar"] + "/>" + "</td>";
                    github_table +="</tr><tr>";
                }
                github_table += "</tr><table>";
                if (url.substring(7) == "world"){
                    $("#world-table").html(github_table);
                }else{
                    $("#china-table").html(github_table);
                }
            } 
        });
    }
    load_table("/githubworld");
    load_table("/githubchina");
});
