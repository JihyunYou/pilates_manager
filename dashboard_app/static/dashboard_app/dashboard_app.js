function setAttendance(attendance)  {
    var calendar = document.getElementById('calendar');

    lesson_id = document.getElementById('attendanceLessonId').textContent;

    $.ajax({
        type: 'GET',
        url: '/set_attendance_by_schedule/',
        data: {
            lesson: lesson_id,
            attendance: attendance
        },
        dataType: 'json',
        success: function(response) {
            data = JSON.parse(response);

            // 성공
            if (data.result) {
//              Button 이 아니라 a tag 이기에 reload 해줌
                location.reload()
            }
            // 실패
            else {
                location.reload()
            }
        },
        error: function(xhr, status, error) {
            alert(error);
        },
        complete: function(data)    {

        }
    });
}

function addWeeklyLesson()  {
    var formData = $('#weeklyLessonForm').serialize();

    $.ajax({
        cache: false,
        url: '/add_weekly_lesson_by_schedule/',
        type: 'POST',
        data: formData,
        success: function(response) {
            data = JSON.parse(response);

            // 성공
            if (data.result) {
//               Button 을 Submit 으로 설정해서 자동 reload
            }
            // 실패
            else {
            //   Button 을 Submit 으로 설정해서 자동 reload
            }

        },
        error: function(xhr, status, error) {
            alert(error);
        },
        complete: function(data)    {
            console.log(data)
        }
    });

}

function addLesson()    {
    var formData = $('#oneLessonForm').serialize();

    $.ajax({
        cache: false,
        url: '/add_lesson_by_schedule/',
        type: 'POST',
        data: formData,
        success: function(response) {
//          Form 입력이 잘못되어 render 을 리턴받을 경우는 Json 이 아님
            try {
                data = JSON.parse(response);

                // 성공
                if (data.result) {
                    location.reload()
                }
                else    {
                    location.reload()
                }
            } catch (e) {
                //  Form 입력이 잘못된 경우
                $('#lessonAddModal').modal('hide');
                $('#lessonAddModalParent').html(response);
                $('#lessonAddModal').modal('show');
            }

        },
        error: function(xhr, status, error) {
            alert(error);
        },
        complete: function(data)    {
            console.log(data)
        }
    });
}

document.addEventListener('DOMContentLoaded', function()    {
    const user_id = JSON.parse(document.getElementById('user_id').textContent);
//    alert(user_id);
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        schedulerLicenseKey: 'CC-Attribution-NonCommercial-NoDerivatives',

        selectable: true,

        timeZone: 'Asia/Seoul',
        locale: 'ko',
        firstDay: 1,
        allDaySlot: false,
        slotMinTime: "06:00:00",
        contentHeight:"auto",
        hiddenDays: [ 0 ],

        slotLabelFormat: {
            hour: '2-digit',
            omitZeroMinute: false,
            hour12: false,
            meridiem: 'short',
        },

        headerToolbar: {
            start: 'dayGridMonth,timeGridWeek,resourceTimeGridDay',
            center: 'title',
            end: 'today prev,next'
        },

        eventTimeFormat: {
            hour: "2-digit",
            minute: "2-digit",
            meridiem: false,
            hour12: false
        },

//        initialView: 'timeGridWeek',

//      ------------------ Vertical Resource View 를 위한 설정
        initialView: 'resourceTimeGridDay',
//      ----------------------------------------------------

//      Resources 설정
        resources: function(fetchInfo, successCallback, failureCallback)   {
            $.ajax({
                type: 'GET',
                url: '/get_dashboard_resources/',
                success: function(response) {
                    data = JSON.parse(response);
//                    console.log(data);
                    successCallback(data);
                },
                complete: function(data)    {

                }
            });
        },

        events: function(fetchInfo, successCallback, failureCallback)   {
            $.ajax({
                type: 'GET',
                url: '/get_dashboard_events/',
                success: function(response) {
                    data = JSON.parse(response);
//                    console.log(data);
                    successCallback(data);
                },
                complete: function(data)    {

                }
            });
        },

        dateClick: function(info) {
            document.getElementById("id_lesson_time").value = ""

            const dtArray = info.dateStr.split("T");
//            document.getElementById("datePicker").value = dtArray[0];
            document.getElementById("id_lesson_date").value = dtArray[0];

//          일간 스케쥴표가 아닌 경우 날짜만 선택되므로 시간은 설정하지 않음
            if (typeof dtArray[1] !== 'undefined') {
                document.getElementById("id_lesson_time").value = dtArray[1];
            }

            $('#lessonAddModal').modal('show');
        },

        eventClick: function(info)  {
            document.getElementById('attendanceLessonId').textContent = info.event.id;
            $('#attendanceChgModal').modal('show');
        }
    });
    calendar.render();
});