function showSchedule(studio_id)    {
    alert(studio_id);
}

document.addEventListener('DOMContentLoaded', function()    {

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
            start: 'dayGridMonth,timeGridWeek,timeGridDay,resourceTimeGridDay',
            center: 'title',
            end: 'today prev,next'
        },

        events: [

        ],
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

        dateClick: function(info) {
            document.getElementById("id_lesson_time").value = ""

            const dtArray = info.dateStr.split("T");
            document.getElementById("datePicker").value = dtArray[0];
            document.getElementById("id_lesson_date").value = dtArray[0];

            if (typeof dtArray[1] !== 'undefined') {
                document.getElementById("id_lesson_time").value = dtArray[1];
            }

            document.getElementById("createButton").click();

        }
    });
    calendar.render();
});