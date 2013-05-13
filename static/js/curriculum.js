$(document).ready(function(){
    $("#query-curriculum").autocomplete({
        minlength: 2,
        max: 5,
        autoFocus: true,
        delay: 50,
        source: function(request, response){
            var url = '/Teac_Course';
            $.ajax({
                type: 'POST',
                url: url,
                data: {
                    'query_string': request.term
                },
                dataType: 'json',
                success: function(data){
                    response($.map(data, function(item){
                        return {
                            label: item,
                            value: item
                        }
                    }));
                }
            });
        }
    });
    function load_course_table(){
        var url = "/curriculum"
        var param = {
            'query_string': $("input[id='query-curriculum']").val()
        }
        var weekday_map = new Array();
        weekday_map[1] = "周一";
        weekday_map[2] = "周二";
        weekday_map[3] = "周三";
        weekday_map[4] = "周四";
        weekday_map[5] = "周五";
        weekday_map[6] = "周六";
        weekday_map[7] = "周日";
        //console.debug(weekday_map);
        $.ajax({
            type: 'POST',
            url: url,
            data: param,
            dataType: 'json',
            success: function(data){
                var course_table = "<table class='table table-striped'>";
                course_table += "<thead><tr>";
                course_table += "<th>课程</th>";
                course_table += "<th>教师</th>";
                course_table += "<th>上课地点</th>";
                course_table += "<th>星期</th>";
                course_table += "<th>节次</th>";
                course_table += "<th>起止周</th>";
                course_table += "</tr></thead>";
                course_table += "<tbody>";
                for (var i in data){
                    course_table += "<tr>";
                    course_table += "<td class='solid'>" + data[i]['course'] + "</td>";
                    course_table += "<td class='solid'>" + data[i]['teacher'] + "</td>";
                    course_table += "<td class='solid'>" + data[i]['addr'] + "</td>";
                    course_table += "<td class='solid'>" + weekday_map[data[i]['weekday']] + "</td>";
                    course_table += "<td class='solid'>" + data[i]['section'] + "</td>";
                    course_table += "<td class='solid'>" + data[i]['startend'] + "</td>";
                    course_table +="</tr>";
                }
                course_table += "</tbody></table>";
                $('#course_table').html(course_table);
            }
        });
    }
    $("#query-curriculum").bind('keyup', function(event){
        if (event.keyCode == "13"){
            load_course_table();
        }
    });

    $('#search-button').click(function(){
       load_course_table();
       return false;
    });

    $('#prompt').popover({
        placement: 'bottom',
        title: '如何使用?',
        content: '在搜索框中输入课程名字或者是教师名字即可以搜索到相关的课程信息',
        trigger: 'hover',
        delay: 0
    });
    //$('#prompt').popover();
});
