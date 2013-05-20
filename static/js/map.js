$('#ChinaMap').SVGMap({
    mapName: 'china',
    stateData: {
        'heilongjiang': {'stateInitColor': 1, 'baifenbi': 0.236},
        'beijing': {'stateInitColor': 2},
        'shanghai': {'stateInitColor': 3},
        'tianjin': {'stateInitColor': 4},
        'sichuan': {'stateInitColor': 5},
        'shandong': {'stateInitColor': 6},
        'shanxi': {'stateInitColor': 3},
        'zhejiang': {'stateInitColor': 4},
        'jiangshu': {'stateInitColor': 2},
        'hunan': {'stateInitColor': 4},
        'guizou': {'stateInitColor': 5},
        'neimenggu': {'stateInitColor': 6},
        'henan': {'stateInitColor': 3},
        'gansu': {'stateInitColor': 4},
        'ningxia': {'stateInitColor': 2},
        'jilin': {'stateInitColor': 1}
    },
    stateTipHtml: function(stateData, obj){
        return 'id:' + ((stateData)[obj.id] && (stateData)[obj.id].baifenbi || obj.id) + '<br/>name:' + obj.name;
    }
});
$('#WorldMap').SVGMap({
    mapName: 'world',
    mapWidth: 600,
    mapHeight: 400
});
