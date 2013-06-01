$(document).ready(function(){

    var polling = function(){
        load_china_map('/chinamapajax', "#ChinaMap");
        load_china_map("/chinamapajax", "#WorldMap");
        console.debug("request");
    }
    interval = setInterval(polling, 10000);
    function load_china_map(url, select){
        $.ajax({
            type: 'POST',
            url: url,
            data: {"site": "Tornado-data"},
            dataType: "json",
            success: function(data){
                console.debug("hello");
                fill_map(data, select);
            }
        });
    }


    function fill_map(data, select){
        $(select).SVGMap({
            mapName: select.substring(1, 6).toLowerCase(),
            stateData: data,
            stateTipHtml: function(stateData, obj){
                return obj.name + ": " + ((stateData)[obj.id] && (stateData)[obj.id].score || "0");
            },
            mapWidth: 720,
            mapHeight: 480
        });
    }


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
                    fill_map(data, select);
                    socket.send(JSON.stringify(data));
                };
                socket.onclose = function(event){
                    socket.close();
                };
            }
            else {
                alert("websocket are not supported in your browser, chose chrome browser or firfox!");
            }
        }
    }
    //var chinamapsocket = new updater("/chinamap", "#ChinaMap");
    //var worldmapsocket = new updater("/worldmap", "#WorldMap");
    //chinamapsocket.start();
    //worldmapsocket.start();

/*
    $('#WorldMap').SVGMap({
        mapName: 'world',
        stateData: {
            'CN': {'stateInitColor': 0, 'score': 0}
        },
        stateTipHtml: function(stateData, obj){
            return obj.name + ": " + ((stateData)[obj.id] && (stateData)[obj.id].score || "0");
        },
        mapWidth: 720,
        mapHeight: 480
    });
*/
});
/*
         {
        'heilongjiang': {'stateInitColor': 0, 'score': 0},
        'liaoning': {'stateInitColor': 1, 'score': 1},
        'neimenggu': {'stateInitColor': 2, 'score': 2},
        'gansu': {'stateInitColor': 3, 'score': 3},
        'sichuan': {'stateInitColor': 4, 'score': 4},
        'shandong': {'stateInitColor': 5, 'score': 5},
        'shanxi': {'stateInitColor': 6, 'score': 6},
        'zhejiang': {'stateInitColor': 7, 'score': 7},
        'jiangshu': {'stateInitColor': 8, 'score': 8}
    },
*/
