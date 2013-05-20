$('#ChinaMap').SVGMap({
    mapName: 'china',
    stateData: {
        'heilongjiang': {'stateInitColor': 1, 'score': 1},
        'beijing': {'stateInitColor': 2, 'score': 0},
        'shanghai': {'stateInitColor': 3, 'score': 0},
        'tianjin': {'stateInitColor': 4, 'score': 0},
        'sichuan': {'stateInitColor': 5, 'score': 0},
        'shandong': {'stateInitColor': 6, 'score': 0},
        'shanxi': {'stateInitColor': 3, 'score': 0},
        'zhejiang': {'stateInitColor': 4, 'score': 0},
        'jiangshu': {'stateInitColor': 2, 'score': 0},
        'hunan': {'stateInitColor': 4, 'score': 0},
        'guizou': {'stateInitColor': 5, 'score': 0},
        'neimenggu': {'stateInitColor': 6, 'score': 0},
        'henan': {'stateInitColor': 3, 'score': 0},
        'gansu': {'stateInitColor': 4, 'score': 0},
        'ningxia': {'stateInitColor': 2, 'score': 0},
        'jilin': {'stateInitColor': 1, 'score': 0}
    },
    stateTipHtml: function(stateData, obj){
        return obj.name + ": " + (stateData)[obj.id].score;
    }
});
$('#WorldMap').SVGMap({
    mapName: 'world',
    mapWidth: 600,
    mapHeight: 400
});
