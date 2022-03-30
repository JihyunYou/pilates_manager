function showStudioDetail(studio)   {
    var $table = $('#teacherListTable');
    $table.bootstrapTable('destroy')

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