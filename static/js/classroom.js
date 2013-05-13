$(document).ready(function(){
    var date = '';
    var maps = {
        "第一节": '0',
        "第二节": '1',
        "第三节": '2',
        "第四节": '3',
        "第五节": '4',
    };

    function formatdate(year, month, day){
        if (month.toString().length == 1){
            month = '0' + month;
        }
        if (day.toString().length == 1){
            day = '0' + day;
        }
        return year + '-' + month + '-' + day;
    }
    //$('.datepicker').datepicker();
    function check_checkbox(){
        var sections = new Array() ;
        $('#sections button').each(function(){
            var section = $(this).text();
            //console.debug(section);
            var classname = $(this).attr('class').split(' ');
            //console.debug(classname);
            //console.debug(classname[classname.length - 1]);
            if (classname[classname.length - 1] == 'active'){
                sections.push(section);
            }
        });
        return sections;
        //console.debug(sections.length);
    }
    
    //在循环中return并不会终止函数,只是终止循环
    function check_building(){
        var builds = new Array();
        $('#buildTab li').each(function(){
            if ($(this).hasClass('active')){
                var buildname = $(this).children('a').text();
                builds.push(buildname);
            }
        });
        return builds;
    }

    $('#dp3').datepicker({format: 'yyyy-mm-dd', weekStart: 1}).on('changeDate', function(ev){
        date = formatdate(ev.date.getFullYear(), ev.date.getMonth() + 1, ev.date.getDate());
        //$('#dp3').datepicker('hide');
        var sections = check_checkbox();
        if (sections.length == 0){
            $('#myModalLabel').html('请选择相应的节次');
            $('#myModal').modal('show');
            return;
        }
        var builds = check_building();
        if(builds.length != 0){
            //console.debug(builds[0]);
            var sections = check_checkbox();
            var num_sections = '';
            for (var i in sections){
                num_sections += maps[sections[i]];
            }
            var url = '/classroom'; 
            param = {
                'date': date,
                "build": builds[0],
                "param": num_sections
            }
            //console.debug(param);
            $.ajax({
                type: 'POST',
                url: url,
                data: param, 
                dataType: 'json',
                success: function(data){
                    var room_table  = "<table class='table table-striped'><tr>";
                    //console.debug(data);
                    //var data = data['roomnames'];
                    for (var i in data){
                       room_table += "<td class='solid'>";
                       room_table += data[i];
                       room_table += "</td>";
                       if ((i + 1) % 3 == 0){
                           room_table += "</tr><tr>";
                       }
                    }
                    room_table += "</tr></table>";
                    $('#room_table').html(room_table);
                }
            });  
        }
        //console.debug(date);
    });

    //点击building 的时候,检查选择的节次并且显示.
    $('#buildTab a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
        var buildname = $(this).text();
        //console.debug(buildname);
        var sections = check_checkbox();
        if (date == ''){
            $('#myModalLabel').html('请选择日期');
            $('#myModal').modal('show');
            return;
        }
        if (sections.length == 0){
            $('#myModalLabel').html('请选择相应的节次');
            $('#myModal').modal('show');
        }else{
            var num_sections = new Array();
            for (var i in sections){
                num_sections += maps[sections[i]];
            }
            var url = '/classroom';
            var param = {
                "date": date,
                "build": buildname,
                "param": num_sections
            };
            //console.debug(param);
            $.ajax({
                type: 'POST',
                url: url, 
                data: param,
                dataType: "json",
                success: function(data){
                    var room_table  = "<table class='table table-striped'><tr>";
                    //console.debug(data);
                    //var data = data['roomnames'];
                    for (var i in data){
                       room_table += "<td class='solid'>";
                       room_table += data[i];
                       room_table += "</td>";
                       if ((i + 1) % 3 == 0){
                           room_table += "</tr><tr>";
                       }
                    }
                    room_table += "</tr></table>";
                    $('#room_table').html(room_table);
                }
            });
        }
    });

    //点击button的时候，检查building是否已经选择, 有则显示，否则不显示
    $('#sections button').click(function(){
        $(this).button('toggle');
        var builds = check_building();
        if (date == ''){
            $('#myModalLabel').html('请选择日期');
            $('#myModal').modal('show');
            return;
        }
        if(builds.length != 0){
            //console.debug(builds[0]);
            var sections = check_checkbox();
            if (sections.length == 0){
                $('#myModal').on('hidden', function(){
                    $('#room_table').html('');
                })
                $('#myModalLabel').html('请选择相应的节次');
                $('#myModal').modal('show');
            }else{
                var num_sections = '';
                for (var i in sections){
                    num_sections += maps[sections[i]];
                }
                var url = '/classroom'; 
                param = {
                    'date': date,
                    "build": builds[0],
                    "param": num_sections
                }
                //console.debug(param);
                $.ajax({
                    type: 'POST',
                    url: url,
                    data: param, 
                    dataType: 'json',
                    success: function(data){
                        var room_table  = "<table class='table table-striped'><tr>";
                        //console.debug(data);
                        //var data = data['roomnames'];
                        for (var i in data){
                           room_table += "<td class='solid'>";
                           room_table += data[i];
                           room_table += "</td>";
                           if ((i + 1) % 3 == 0){
                               room_table += "</tr><tr>";
                           }
                        }
                        room_table += "</tr></table>";
                        $('#room_table').html(room_table);
                    }
                });  
            }
        }
    });
});
