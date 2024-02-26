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
            curve: 'straight',
            width: 3.5
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
        },
        yaxis: {
            min: y_min,
            max: y_max,
            title: {
                text: yaxis_title,
                style: {
                    fontSize: '12px'
                }
            }
        },
        theme: {
            palette: 'palette7'
        }
    };

    if (y_limit !== undefined) {
        options['annotations'] = {
            yaxis: [
                {
                    y: y_limit,
                    y2: y_max,
                    fillColor: '#EED202',
                    label: {
                        borderColor: '#EED202',
                        style: {
                            color: '#fff',
                            background: '#EED202'
                        },
                        text: 'Пределно допустима концентрация ' + y_limit
                    }
                }
            ]
        }

    }

    var chart = new ApexCharts(document.querySelector("#plot"), options);
    chart.render();
});