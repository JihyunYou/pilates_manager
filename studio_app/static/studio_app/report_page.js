//  현황 집계 화면
var yearReportLineChart;
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function(){
        year = new Date().getFullYear();
        setYearReportTable(year);
    }, 100);

});

function changeReportYear(opt)  {
    displayYear = document.getElementById('reportYear');
    yearValue = parseInt(displayYear.innerHTML);

    if(opt == 'down') {
        yearValue -= 1;
    } else  {
        yearValue += 1;
    }

    displayYear.innerHTML = yearValue;
    setYearReportTable(yearValue);
}

function setYearReportTable(year)   {
    var tableRowNum = 5;
    var $yearReportTable = $('#yearReportTable');
    $yearReportTable.bootstrapTable('destroy');

    $.ajax({
        type: 'GET',
        url: '/get_year_report/',
        data: {
            year: year
        },
        dataType: 'json',
        success: function(response) {
            data = JSON.parse(response);
            console.log(data);

            // Return 값은 [{table용 데이터}, {chart용 데이터}] 의 형태
            var dataArray = [];
            for(var i=0; i<tableRowNum; i++)
                dataArray.push(data[i]);

            // Table
            $yearReportTable.bootstrapTable(
                {
                    data: dataArray
                }
            );
            // Chart
            if(yearReportLineChart != null){
               yearReportLineChart.destroy();
            }
            var ctx = document.getElementById('yearReportLineChart').getContext('2d');
            yearReportLineChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
                    datasets: [
                        {
                            label: '월 매출 계',
                            data: Object.values(data[tableRowNum]),
                            fill: false,
                            borderColor: 'rgb(248, 3, 3)',
                            tension: 0.1
                        },
                        {
                            label: '월 신규 등록 계',
                            data: Object.values(data[tableRowNum+1]),
                            fill: false,
                            borderColor: 'rgb(248, 148, 3)',
                            tension: 0.1
                        },
                        {
                            label: '월 재등록 계',
                            data: Object.values(data[tableRowNum+2]),
                            fill: false,
                            borderColor: 'rgb(248, 248, 3)',
                            tension: 0.1
                        }
                    ]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        },
        complete: function(data)    {

        }
    });
}