function showStudioDetail(studio_id, studio_name)   {
    // 지점 선택시 소속 강사, 소속 회원 출력 부분에 지점 표시
    var targets = document.getElementsByClassName('selected-studio');
    for (var i=0; i<targets.length; i++)    {
        targets[i].firstChild.data = studio_name
    }

    var $teacherTable = $('#teacherListTable');
    $teacherTable.bootstrapTable('destroy');
    $.ajax({
        type: 'GET',
        url: '/get_teachers_of_selected_studio/',
        data: {
            studio: studio_id
        },
        dataType: 'json',
        success: function(response) {
            data = JSON.parse(response);
            console.log(data);

            $teacherTable.bootstrapTable(
                {
//                    data-pagination: ture,
                    data: data
                }
            );
        },
        complete: function(data)    {

        }
    });

    var $memberTable = $('#memberListTable');
    $memberTable.bootstrapTable('destroy');
    $.ajax({
        type: 'GET',
        url: '/get_members_of_selected_studio/',
        data: {
            studio: studio_id
        },
        dataType: 'json',
        success: function(response) {
            data = JSON.parse(response);
            console.log(data);

            $memberTable.bootstrapTable(
                {
                    data: data
                }
            );
        },
        complete: function(data)    {

        }
    });
}

function showMemberDetail(member_id, member_name)   {
    var targets = document.getElementsByClassName('selected-member');
    for (var i=0; i<targets.length; i++)    {
        targets[i].firstChild.data = member_name
    }

    var addBtn = document.getElementById('selected-member-add-btn');
    addBtn.href = member_id + '/membership/add/';
    addBtn.classList.remove('disabled');

    var $table = $('#membershipTable');
    $table.bootstrapTable('destroy');

    $.ajax({
        type: 'GET',
        url: '/get_membership_of_selected_member/',
        data: {
            member: member_id
        },
        dataType: 'json',
        success: function(response) {
            data = JSON.parse(response);
            console.log(data);

            $table.bootstrapTable(
                {
//                    data-pagination: ture,
                    data: data
                }
            );
        },
        complete: function(data)    {

        }
    });
}