$(document).ready(function(){
    $("#myTab a").click(function(e){
        e.preventDefault();
        $(this).tab("show");
    })
    var polling = function(){
        load_table("/githubworld", "#world-table");
        load_table("/githubchina", "#china-table");
    }
    //polling();
    //interval = setInterval(polling, 60000);

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
    var chinasocket = new updater("/socketchina", "#china-table");
    var worldsocket = new updater("/socketworld", "#world-table");
    chinasocket.start();
    worldsocket.start();

    function fill_table(data, select){
        if (data.length == 0){
            $(select).html("<div class='progress progress-striped active'><div class='bar' style='width: 40%;'></div></div>");
        }else{
            $(select).empty();
            var github_table  = $("<table class='table table-striped'>");
            github_table.appendTo(select);
            var head = $("<thead>");
            head.appendTo(github_table);
            var tr = $("<tr>");
            tr.appendTo(head);

            $("<th>Rank</th>").appendTo(tr);
            $("<th>Name</th>").appendTo(tr);
            $("<th>Score</th>").appendTo(tr);
            $("<th>Language</th>").appendTo(tr);
            $("<th>Location</th>").appendTo(tr);
            $("<th>Profile</th>").appendTo(tr);
            for (var i in data){
                var tr = $("<tr>");
                tr.appendTo(github_table);
                var count = parseInt(i) + 1;
                $("<td class='solid'>#" + count + "</td>").appendTo(tr);
                $("<td class='solid'>" + "<a href='https://github.com/" + data[i]["login"] + "' target='_blank'>" + data[i]["login"] + "</a>" + "&nbsp(" + data[i]["name"] + ")" + "</td>").appendTo(tr);
                $("<td class='solid'>" + parseInt(data[i]["score"]) + "</td>").appendTo(tr);
                $("<td class='solid'>" + data[i]["language"] + "</td>").appendTo(tr);
                $("<td class='solid'>" + data[i]["location"] + "</td>").appendTo(tr);
                $("<td class='solid'>" + "<img height='48' width='48' src=" + data[i]["gravatar"] + "/>" + "</td>").appendTo(tr);
            }
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
