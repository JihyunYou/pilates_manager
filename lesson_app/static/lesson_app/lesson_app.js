function showAttendance(lesson_id, lesson_date, lesson_time)  {
    // 지점 선택시 소속 강사, 소속 회원 출력 부분에 지점 표시
    var targets = document.getElementsByClassName('selected-lesson');
    for (var i=0; i<targets.length; i++)    {
        targets[i].firstChild.data = lesson_date + ' ' + lesson_time + ' 수업'
    }

    var $attendanceTable = $('#attendanceTable');
    $attendanceTable.bootstrapTable('destroy');
    $.ajax({
        type: 'GET',
        url: '/get_attendance_of_selected_lesson/',
        data: {
            lesson: lesson_id
        },
        dataType: 'json',
        success: function(response) {
            data = JSON.parse(response);
            console.log(data);

            $attendanceTable.bootstrapTable(
                {
                    data: data
                }
            );
        },
        complete: function(data)    {

        }
    });
}

function setAttendance(attendance_id, status)   {
    $.ajax({
        type: 'GET',
        url: '/set_attendance/',
        data: {
            attendance: attendance_id,
            status: status
        },
        dataType: 'json',
        success: function(response) {
            alert(response)
            location.reload()
        },
        complete: function(data)    {

        }
    });
}