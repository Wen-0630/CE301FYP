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

            // Handle the special case where currentValue is 0
            if (currentValue === 0) {
                // Set the gauge value to zero and make sure no extra pointers are added
                chart_gauge_01.set(0);
                chart_gauge_01.setOptions({
                    pointer: {
                        length: 0.75, 
                        strokeWidth: 0.042, 
                        color: '#1D212A' 
                    }
                });
            } else {
                chart_gauge_01.set(currentValue); 
            }

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

    // Manual verification data for radar chart
    // var radarData = {
    //     selected_category_names: ["Food", "Shopping", "Transport"],
    //     budget_categories: [
    //         { category_name: "Food", budgeted_amount: 6000, actual_spending: 5000 },
    //         { category_name: "Shopping", budgeted_amount: 16000, actual_spending: 14000 },
    //         { category_name: "Transport", budgeted_amount: 30000, actual_spending: 28000 }
    //     ]
    // };

    // echart Radar
    $(document).ready(function() {
        $.ajax({
            url: "/api/radar_data",
            type: "GET",
            dataType: "json",
            success: function(radarData) {
                // Check if radarData is properly fetched
                console.log('Fetched radarData:', radarData);
                
                // Proceed to render the radar chart using the fetched data
                if ($('#echart_sonar').length && radarData) {
                    var selectedCategories = radarData.indicators
                        .filter(indicator => indicator.max > 0)  // Only include categories with a non-zero budget
                        .map(indicator => indicator.text);
                    
                    console.log('selectedCategories:', selectedCategories); // Debugging statement to check selectedCategories

                    var indicators = radarData.indicators.filter(indicator => indicator.max > 0);
                    var actualSpendings = radarData.actual_values.slice(0, indicators.length);
                    var budgetValues = radarData.budget_values.slice(0, indicators.length);

                    // Format the values to two decimal places
                    var formattedBudgetValues = budgetValues.map(value => parseFloat(value).toFixed(2));
                    var formattedActualSpendings = actualSpendings.map(value => parseFloat(value).toFixed(2));

                    var echartRadar = echarts.init(document.getElementById('echart_sonar'), theme);

                    echartRadar.setOption({
                        title: [
                            {
                                text: 'Categories as below:',
                            },
                            {
                                subtext: `From ${radarData.start_date} to ${radarData.end_date}`,
                                left: 'left',     // Align the subtext to the left
                                bottom: '0%',     // Position the subtext at the bottom
                                textAlign: 'left',
                                subtextStyle: {
                                    fontSize: 12  // Adjust the font size as needed
                                }
                            }
                        ],
                        tooltip: {
                            trigger: 'item'
                        },
                        legend: {
                            orient: 'vertical',
                            x: 'right',
                            y: 'bottom',
                            data: ['Budgeted Amount', 'Actual Spending']
                        },
                        polar: [{
                            indicator: indicators
                        }],
                        series: [{
                            name: 'Budget vs Spending',
                            type: 'radar',
                            data: [{
                                value: formattedBudgetValues,
                                name: 'Budgeted Amount'
                            }, {
                                value: formattedActualSpendings,
                                name: 'Actual Spending'
                            }]
                        }]
                    });
                } else {
                    console.log('No radar data available or no radarData defined.');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error fetching radar data:', error);
            }
        });
    });

    



    // echart Gauge
    if ($('#echart_gauge').length) {
        var incomeExpenseRatio = $('#echart_gauge').data('ratio');

        var echartGauge = echarts.init(document.getElementById('echart_gauge'), theme);

        echartGauge.setOption({
            tooltip: {
                formatter: "{a} <br/>{b} : {c}%"
            },
            // toolbox: {
            //     show: true,
            //     feature: {
            //         restore: {
            //             show: true,
            //             title: "Restore"
            //         },
            //         saveAsImage: {
            //             show: true,
            //             title: "Save Image"
            //         }
            //     }
            // },
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
                        color: '#ccc'
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
