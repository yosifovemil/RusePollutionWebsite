$(document).ready(function(){
    var options = {
        series: y_vals,
        chart: {
            height: 0.7 * window.innerHeight,
            type: chart_type,
            zoom: {
                enabled: false
            }
        },
        stroke: {
            curve: 'straight'
        },
        title: {
            text: title_text,
            align: 'center'
        },
        grid: {
            row: {
                colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
                opacity: 0.5
            },
        },
        xaxis: {
            type: 'datetime',
            categories: x_vals
        },
        tooltip: {
            x: {
                format: "dd/MMM/yyyy HH:mm"
            }
        }
    };

    var chart = new ApexCharts(document.querySelector("#plot"), options);
    chart.render();
});