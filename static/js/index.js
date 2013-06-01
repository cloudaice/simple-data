$(document).ready(function(){
    $("#myTab a").click(function(e){
        e.preventDefault();
        $(this).tab("show");
    })
    var polling = function(){
        load_table("/githubworld", "#world-table");
        load_table("/githubchina", "#china-table");
    }
    interval = setInterval(polling, 10000);

    var updater = function(url, select) {
        this.select = select;
        this.url = "ws://" + location.host + url;
        this.start = function(){
            if ("WebSocket" in window) {
                this.socket = new WebSocket(this.url);
            } 
            else if ("MozWebSocket" in window){
                this.socket = new MozWebSocket(this.url);
            }
            if (this.socket != null){
                var socket = this.socket;
                var select = this.select;
                socket.onmessage = function(event) {
                    var data = JSON.parse(event.data);
                    fill_table(data, select)
                    socket.send(JSON.stringify(data));
                };
                socket.onclose = function(event) {
                    socket.close();
                };
            }
            else {
                alert("websocket are not supported in your browser, chose chrome browser or firfox!");
            }
        }
    }
    //var chinasocket = new updater("/socketchina", "#china-table");
    //var worldsocket = new updater("/socketworld", "#world-table");
    //chinasocket.start();
    //worldsocket.start();

    function fill_table(data, select){
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
        if (data.length == 0){
            $(select).html("<div class='progress progress-striped active'><div class='bar' style='width: 40%;'></div></div>");
        }else{
            $(select).html(github_table);
        }
    }

    function load_table(url, select){
        $.ajax({
            type: 'POST',
            url: url,
            data: {"site": "Tornado-data"},
            dataType: "json",
            success: function(data){
                var select = null;
                if (url.substring(7) == "world"){
                    select = "#world-table";
                }else{
                    select = "#china-table";
                }
                fill_table(data, select);
            } 
        });
    }
});
