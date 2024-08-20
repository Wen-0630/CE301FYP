function init_gauge() {
    if (typeof (Gauge) === 'undefined') { 
        console.log('Gauge.js library not found!');
        return; 
    }

    console.log('init_gauge [' + $('.gauge-chart').length + ']');

    var chart_gauge_settings = {
        lines: 12, 
        angle: 0, // Angle of the gauge arc for a semicircle
        lineWidth: 0.4, 
        pointer: {
            length: 0.75, 
            strokeWidth: 0.042, 
            color: '#1D212A' 
        },
        limitMax: true, 
        colorStart: '#1ABC9C', 
        colorStop: '#1ABC9C', 
        strokeColor: '#F0F3F3', 
        generateGradient: true 
    };

    if ($('#chart_gauge_01').length) {
        console.log('Initializing Gauge...');
        var chart_gauge_01_elem = document.getElementById('chart_gauge_01');
        chart_gauge_01 = new Gauge(chart_gauge_01_elem).setOptions(chart_gauge_settings);

        var maxValue = parseFloat($('#chart_gauge_01').data('max-value'));
        var currentValue = parseFloat($('#chart_gauge_01').data('current-value'));

        console.log('Max Value:', maxValue);
        console.log('Current Value:', currentValue);

        if (!isNaN(maxValue) && !isNaN(currentValue)) {
            chart_gauge_01.maxValue = maxValue; 
            chart_gauge_01.animationSpeed = 32; 

            // Ensure currentValue does not exceed maxValue
            if (currentValue > maxValue) {
                currentValue = maxValue;
            }

            // Set the gauge value
            chart_gauge_01.set(currentValue); 

            // If the completion is 100%, change the color to fully green
            if (currentValue === maxValue) {
                chart_gauge_01.setOptions({
                    colorStart: '#1ABC9C',
                    colorStop: '#1ABC9C',
                    strokeColor: '#1ABC9C'
                });
            }
        } else {
            console.error('Invalid values for max or current value.');
        }
    }
};

function init_echarts() {

    if (typeof (echarts) === 'undefined') { 
        console.log('ECharts library not found!');
        return; 
    }
    console.log('init_echarts');

    var theme = {
        color: [
            '#26B99A', '#34495E', '#BDC3C7', '#3498DB',
            '#9B59B6', '#8abb6f', '#759c6a', '#bfd3b7'
        ],
        title: {
            itemGap: 8,
            textStyle: {
                fontWeight: 'normal',
                color: '#408829'
            }
        },
        toolbox: {
            color: ['#408829', '#408829', '#408829', '#408829']
        },
        tooltip: {
            backgroundColor: 'rgba(0,0,0,0.5)',
            axisPointer: {
                type: 'line',
                lineStyle: {
                    color: '#408829',
                    type: 'dashed'
                },
                crossStyle: {
                    color: '#408829'
                },
                shadowStyle: {
                    color: 'rgba(200,200,200,0.3)'
                }
            }
        },
        grid: {
            borderWidth: 0
        },
        categoryAxis: {
            axisLine: {
                lineStyle: {
                    color: '#408829'
                }
            },
            splitLine: {
                lineStyle: {
                    color: ['#eee']
                }
            }
        },
        valueAxis: {
            axisLine: {
                lineStyle: {
                    color: '#408829'
                }
            },
            splitLine: {
                lineStyle: {
                    color: ['#eee']
                }
            }
        },
        textStyle: {
            fontFamily: 'Arial, Verdana, sans-serif'
        }
    };

    // echart Radar
    if ($('#echart_sonar').length) {
        var echartRadar = echarts.init(document.getElementById('echart_sonar'), theme);

        echartRadar.setOption({
            title: {
                text: 'Budget vs spending',
                subtext: 'Subtitle'
            },
            tooltip: {
                trigger: 'item'
            },
            legend: {
                orient: 'vertical',
                x: 'right',
                y: 'bottom',
                data: ['Allocated Budget', 'Actual Spending']
            },
            toolbox: {
                show: true,
                feature: {
                    restore: {
                        show: true,
                        title: "Restore"
                    },
                    saveAsImage: {
                        show: true,
                        title: "Save Image"
                    }
                }
            },
            polar: [{
                indicator: [{
                    text: 'Sales',
                    max: 6000
                }, {
                    text: 'Administration',
                    max: 16000
                }, {
                    text: 'Information Techology',
                    max: 30000
                }, {
                    text: 'Customer Support',
                    max: 38000
                }, {
                    text: 'Development',
                    max: 52000
                }, {
                    text: 'Marketing',
                    max: 25000
                }]
            }],
            calculable: true,
            series: [{
                name: 'Budget vs spending',
                type: 'radar',
                data: [{
                    value: [4300, 10000, 28000, 35000, 50000, 19000],
                    name: 'Allocated Budget'
                }, {
                    value: [5000, 14000, 28000, 31000, 42000, 21000],
                    name: 'Actual Spending'
                }]
            }]
        });
    }

    // echart Gauge
    if ($('#echart_gauge').length) {
        var incomeExpenseRatio = $('#echart_gauge').data('ratio');

        var echartGauge = echarts.init(document.getElementById('echart_gauge'), theme);

        echartGauge.setOption({
            tooltip: {
                formatter: "{a} <br/>{b} : {c}%"
            },
            toolbox: {
                show: true,
                feature: {
                    restore: {
                        show: true,
                        title: "Restore"
                    },
                    saveAsImage: {
                        show: true,
                        title: "Save Image"
                    }
                }
            },
            series: [{
                name: 'Income vs. Expense Ratio',
                type: 'gauge',
                center: ['50%', '50%'],
                startAngle: 140,
                endAngle: -140,
                min: 0,
                max: 200,
                precision: 0,
                splitNumber: 10,
                axisLine: {
                    show: true,
                    lineStyle: {
                        color: [
                            [0.3, 'lightgreen'], // Green Zone
                            [0.5, 'orange'],     // Yellow Zone
                            [0.7, 'skyblue'],    // Blue Zone
                            [1, '#ff4500']       // Red Zone
                        ],
                        width: 30
                    }
                },
                axisTick: {
                    show: true,
                    splitNumber: 5,
                    length: 8,
                    lineStyle: {
                        color: '#eee',
                        width: 1,
                        type: 'solid'
                    }
                },
                axisLabel: {
                    show: true,
                    formatter: function (v) {
                        if (v === 0) return 'Surplus';
                        if (v === 80) return 'Catching';
                        if (v === 100) return 'Break-even';
                        if (v === 120) return 'Mild Deficit';
                        if (v === 200) return 'Critical Deficit';
                        return '';
                    },
                    textStyle: {
                        color: '#333'
                    }
                },
                splitLine: {
                    show: true,
                    length: 30,
                    lineStyle: {
                        color: '#eee',
                        width: 2,
                        type: 'solid'
                    }
                },
                pointer: {
                    length: '80%',
                    width: 8,
                    color: 'auto'
                },
                title: {
                    show: true,
                    offsetCenter: ['-65%', -10],
                    textStyle: {
                        color: '#333',
                        fontSize: 15
                    }
                },
                detail: {
                    show: true,
                    backgroundColor: 'rgba(0,0,0,0)',
                    borderWidth: 0,
                    borderColor: '#ccc',
                    width: 100,
                    height: 40,
                    offsetCenter: ['-60%', 10],
                    formatter: '{value}%',
                    textStyle: {
                        color: 'auto',
                        fontSize: 20
                    }
                },
                data: [{
                    value: incomeExpenseRatio,
                    name: 'Income vs. Expense'
                }]
            }]
        });
    }
};

$(document).ready(function () {
    $('#menu_toggle').on('click', function () {
        $('body').toggleClass('nav-md nav-sm');
    });

    init_gauge(); // Initialize the Gauge.js when the document is ready
    init_echarts(); // Initialize the ECharts when the document is ready
});
