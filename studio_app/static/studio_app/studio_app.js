function showStudioDetail(studio)   {
    var $table = $('#teacherListTable');
    $table.bootstrapTable('destroy');

    $.ajax({
        type: 'GET',
        url: '/get_teachers_of_selected_studio/',
        data: {
            studio: studio
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