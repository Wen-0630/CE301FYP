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
                                left: 'left',    
                                bottom: '0%',     
                                textAlign: 'left',
                                subtextStyle: {
                                    fontSize: 12  
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
                    if ($('#echart_sonar').length) {
                        $('#echart_sonar').text('No active budget. Please set a budget.');
                    }
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

    if ($('#echart_pie').length) {
        var echartPie = echarts.init(document.getElementById('echart_pie'), theme);
    
        // Fetch data for income categories from the API
        $.ajax({
            url: '/api/income_categories_data',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                console.log('Income categories data:', response);
    
                // Check if there are no categories or values
                if (response.categories.length === 0 || response.values.length === 0) {
                    console.log('No income data available for the current month.');
                    $('#echart_pie').text('No income data available for the current month.');
                    return;  // Exit if there's no data to display
                }
    
                // Proceed with rendering the chart if data is available
                echartPie.setOption({
                    tooltip: {
                        trigger: 'item',
                        formatter: "{a} <br/>{b} : {c} ({d}%)"
                    },
                    legend: {
                        x: 'center',
                        y: 'bottom',
                        data: response.categories
                    },
                    toolbox: {
                        show: true,
                        feature: {
                            magicType: {
                                show: true,
                                type: ['pie', 'funnel'],
                                option: {
                                    funnel: {
                                        x: '25%',
                                        width: '50%',
                                        funnelAlign: 'left',
                                        max: 1548
                                    }
                                }
                            },
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
                    calculable: true,
                    series: [{
                        name: 'Income Source',
                        type: 'pie',
                        radius: '55%',
                        center: ['50%', '48%'],
                        data: response.categories.map((category, index) => ({
                            value: response.values[index],
                            name: category
                        }))
                    }]
                });
            },
            error: function(xhr, status, error) {
                console.error('Error fetching income categories data:', error);
                $('#echart_pie').text('Error loading data. Please try again.');
            }
        });
    
        // Original dataStyle and placeHolderStyle definitions remain, even if not directly used
        var dataStyle = {
            normal: {
                label: {
                    show: false
                },
                labelLine: {
                    show: false
                }
            }
        };
    
        var placeHolderStyle = {
            normal: {
                color: 'rgba(0,0,0,0)',
                label: {
                    show: false
                },
                labelLine: {
                    show: false
                }
            },
            emphasis: {
                color: 'rgba(0,0,0,0)'
            }
        };
    }    

    if ($('#echart_donut').length) {
        var echartDonut = echarts.init(document.getElementById('echart_donut'), theme);
    
        // Fetch data for expense categories from the API
        $.ajax({
            url: '/api/expense_categories_data',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                console.log('Expense categories data:', response);
    
                // Check if there are no categories or values
                if (response.categories.length === 0 || response.values.length === 0) {
                    console.log('No expense data available for the current month.');
                    $('#echart_donut').text('No expense data available for the current month.');
                    return;  // Exit if there's no data to display
                }
    
                // Proceed with rendering the chart if data is available
                echartDonut.setOption({
                    tooltip: {
                        trigger: 'item',
                        formatter: "{a} <br/>{b} : {c} ({d}%)"
                    },
                    calculable: true,
                    legend: {
                        x: 'center',
                        y: 'bottom',
                        data: response.categories  // Dynamic legend based on expense categories
                    },
                    toolbox: {
                        show: true,
                        feature: {
                            magicType: {
                                show: true,
                                type: ['pie', 'funnel'],
                                option: {
                                    funnel: {
                                        x: '25%',
                                        width: '50%',
                                        funnelAlign: 'center',
                                        max: 1548
                                    }
                                }
                            },
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
                        name: 'Expense Category',
                        type: 'pie',
                        radius: ['35%', '55%'],  // Set to donut style
                        itemStyle: {
                            normal: {
                                label: {
                                    show: true
                                },
                                labelLine: {
                                    show: true
                                }
                            },
                            emphasis: {
                                label: {
                                    show: true,
                                    position: 'center',
                                    textStyle: {
                                        fontSize: '14',
                                        fontWeight: 'normal'
                                    }
                                }
                            }
                        },
                        data: response.categories.map((category, index) => ({
                            value: response.values[index],
                            name: category
                        }))
                    }]
                });
            },
            error: function(xhr, status, error) {
                console.error('Error fetching expense categories data:', error);
                $('#echart_donut').text('Error loading data. Please try again.');
            }
        });
    }
    

    if ($('#echart_pie2').length) {

        var echartPieCollapse = echarts.init(document.getElementById('echart_pie2'), theme);
    
        fetch('/api/asset_allocation')
            .then(response => response.json())
            .then(data => {
                if (data.error || !data.asset_allocation || data.asset_allocation.length === 0) {
                    // Handle case where no asset allocation is available
                    console.error("Asset Allocation Error:", data.error || "No assets available for allocation.");
                    document.getElementById('echart_pie2').innerHTML = '<p>No assets available for allocation.</p>';
                    return;
                }
    
                // Extract allocation and portfolio type
                const { asset_allocation, portfolio_type } = data;
                
                echartPieCollapse.setOption({
                    title: {
                        text: 'Asset Allocation',
                        subtext: `Portfolio Type: ${portfolio_type}`,  // Display portfolio type as subtitle
                        // x: 'center'
                    },
                    tooltip: {
                        trigger: 'item',
                        formatter: "{a} <br/>{b} : {c} ({d}%)"
                    },
                    legend: {
                        x: 'center',
                        y: 'bottom',
                        data: asset_allocation.map(item => item.name)
                    },
                    toolbox: {
                        show: true,
                        feature: {
                            magicType: {
                                show: true,
                                type: ['pie', 'funnel']
                            },
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
                    calculable: true,
                    series: [{
                        name: 'Asset Allocation',
                        type: 'pie',
                        radius: [25, 90],
                        center: ['50%', 170],
                        roseType: 'area',
                        data: asset_allocation.map(item => ({
                            value: item.value,
                            name: item.name
                        }))
                    }]
                });
            })
            .catch(error => console.error('Error fetching asset allocation:', error));
    }    
       
    if ($('#mainb').length) {
        var echartBar = echarts.init(document.getElementById('mainb'), theme);
    
        // Fetch monthly income and expense data from the API
        $.ajax({
            url: '/api/monthly_income_expense',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.error) {
                    console.error("Error fetching data:", response.error);
                    $('#mainb').text('Error loading data. Please try again.');
                    return;
                }
    
                // Prepare the data for the bar chart
                var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                var incomeData = response.income;
                var expenseData = response.expense;
    
                // Update echartBar options with dynamic data
                echartBar.setOption({
                    title: {
                        text: 'Monthly Income and Expense',
                        subtext: 'Current Year'
                    },
                    tooltip: {
                        trigger: 'axis'
                    },
                    legend: {
                        data: ['Income', 'Expense']
                    },
                    toolbox: {
                        show: false
                    },
                    calculable: false,
                    xAxis: [{
                        type: 'category',
                        data: months
                    }],
                    yAxis: [{
                        type: 'value'
                    }],
                    series: [{
                        name: 'Income',
                        type: 'bar',
                        data: incomeData,
                        markPoint: {
                            data: [{
                                type: 'max',
                                name: 'Max'
                            }, {
                                type: 'min',
                                name: 'Min'
                            }]
                        },
                        markLine: {
                            data: [{
                                type: 'average',
                                name: 'Average'
                            }]
                        }
                    }, {
                        name: 'Expense',
                        type: 'bar',
                        data: expenseData,
                        markPoint: {
                            data: [{
                                type: 'max',
                                name: 'Max'
                            }, {
                                type: 'min',
                                name: 'Min'
                            }]
                        },
                        markLine: {
                            data: [{
                                type: 'average',
                                name: 'Average'
                            }]
                        }
                    }]
                });
            },
            error: function(xhr, status, error) {
                console.error('Error fetching monthly income and expense data:', error);
                $('#mainb').text('Error loading data. Please try again.');
            }
        });
    }

    if ($('#echart_line').length) {
        var echartLine = echarts.init(document.getElementById('echart_line'), theme);
    
        // Fetch holdings data over time from the API
        $.ajax({
            url: '/api/holdings_over_time',
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                if (response.error) {
                    console.error("Error fetching data:", response.error);
                    $('#echart_line').text('Error loading data. Please try again.');
                    return;
                }
    
                // Extract data for the chart
                var months = response.months;
                var stockTotals = response.stock_totals;
                var cryptoTotals = response.crypto_totals;
    
                // Set options for the line chart
                echartLine.setOption({
                    title: {
                        text: 'Holdings Over Time',
                        subtext: 'Last 6 Months'
                    },
                    tooltip: {
                        trigger: 'axis'
                    },
                    legend: {
                        data: ['Stock', 'Crypto']
                    },
                    toolbox: {
                        show: true,
                        feature: {
                            magicType: {
                                show: true,
                                title: {
                                    line: 'Line',
                                    bar: 'Bar',
                                    stack: 'Stack',
                                    tiled: 'Tiled'
                                },
                                type: ['line', 'bar', 'stack', 'tiled']
                            },
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
                    calculable: true,
                    xAxis: [{
                        type: 'category',
                        boundaryGap: false,
                        data: months  // Use dynamic month data
                    }],
                    yAxis: [{
                        type: 'value'
                    }],
                    series: [{
                        name: 'Stock',
                        type: 'line',
                        smooth: true,
                        itemStyle: {
                            normal: {
                                areaStyle: {
                                    type: 'default'
                                }
                            }
                        },
                        data: stockTotals  // Use dynamic stock data
                    }, {
                        name: 'Crypto',
                        type: 'line',
                        smooth: true,
                        itemStyle: {
                            normal: {
                                areaStyle: {
                                    type: 'default'
                                }
                            }
                        },
                        data: cryptoTotals  // Use dynamic crypto data
                    }]
                });
            },
            error: function(xhr, status, error) {
                console.error('Error fetching holdings data:', error);
                $('#echart_line').text('Error loading data. Please try again.');
            }
        });
    }    
};

function init_chart_doughnut() {
    console.log('init_chart_doughnut() is being called');

    if (typeof (Chart) === 'undefined') {
        console.log('Chart.js library not found!');
        return;
    }

    if ($('.canvasDoughnut').length) {
        fetch('/api/top_asset_categories')
            .then(response => response.json())
            .then(data => {
                console.log('Data fetched successfully:', data);

                var topAssetCategories = data.top_asset_categories;
                var totalAmount = data.total_amount;

                if (!Array.isArray(topAssetCategories) || topAssetCategories.length === 0 || totalAmount === 0) {
                    console.log('No asset categories available to display.');
                    return;
                }

                var labels = topAssetCategories.map(category => category.category);
                var values = topAssetCategories.map(category => parseFloat(((category.amount / totalAmount) * 100).toFixed(2)));

                // Define the same color scheme for both the chart and the fa icons
                var backgroundColors = [
                    "#BDC3C7", "#9B59B6", "#E74C3C", "#26B99A", "#3498DB"
                ].slice(0, values.length);

                var chart_doughnut_settings = {
                    type: 'doughnut',
                    tooltipFillColor: "rgba(51, 51, 51, 0.55)",
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: backgroundColors,  // Apply the background color array
                            hoverBackgroundColor: [
                                "#CFD4D8", "#B370CF", "#E95E4F", "#36CAAB", "#49A9EA"
                            ].slice(0, values.length)
                        }]
                    },
                    options: {
                        tooltips: {
                            callbacks: {
                                label: function (tooltipItem, data) {
                                    var dataset = data.datasets[tooltipItem.datasetIndex];
                                    var currentValue = dataset.data[tooltipItem.index]; // Get percentage
                                    var label = data.labels[tooltipItem.index]; // Get category label
                                    return label + ': ' + currentValue + '%';  // Append percentage symbol in tooltip
                                }
                            }
                        },
                        legend: false,
                        responsive: true
                    }
                };

                // Initialize each doughnut chart
                $('.canvasDoughnut').each(function () {
                    var chart_element = $(this);
                    new Chart(chart_element, chart_doughnut_settings);
                });

                // Assign colors to the category icons (fa-square)
                $('.tile_info .fa-square').each(function (index) {
                    if (backgroundColors[index]) {
                        $(this).css('color', backgroundColors[index]);
                    }
                });

            })
            .catch(error => {
                console.error('Error fetching top asset categories:', error);
            });
    } else {
        console.log('No canvasDoughnut elements found on the page');
    }
}

// Function to update the chart with new data (move outside init_charts to make it global)
function updateProfitLossChart(startDate, endDate, hourlyMode = false) {
    $.ajax({
        url: '/api/profit_loss_over_time',
        method: 'GET',
        data: { 
            start_date: startDate.format(hourlyMode ? 'YYYY-MM-DDTHH:mm:ss' : 'YYYY-MM-DD'),  // Use full ISO for hourly, date-only for daily
            end_date: endDate.format(hourlyMode ? 'YYYY-MM-DDTHH:mm:ss' : 'YYYY-MM-DD'),
            hourly_mode: hourlyMode  // Indicate whether hourly mode is enabled
        },
        success: function(response) {
            if (response.error) {
                alert(response.error);
                return;
            }

            const dates = response.map(item => item.date);
            const profitLossValues = response.map(item => parseFloat(item.profit_loss).toFixed(2));

            lineChart.data.labels = dates;
            lineChart.data.datasets[0].data = profitLossValues;
            lineChart.update();
        },
        error: function(err) {
            console.error('Error fetching data', err);
        }
    });
}



function init_charts() {
    if ($('#lineChart').length) {

        // Initialize the chart
        var ctx = document.getElementById("lineChart").getContext('2d');
        window.lineChart = new Chart(ctx, {  // Make lineChart global for access in update function
            type: 'line',
            data: {
                labels: [],  // We will dynamically update these labels (dates)
                datasets: [{
                    label: "Crypto's Profit/Loss",
                    backgroundColor: "rgba(38, 185, 154, 0.31)",
                    borderColor: "rgba(38, 185, 154, 0.7)",
                    pointBorderColor: "rgba(38, 185, 154, 0.7)",
                    pointBackgroundColor: "rgba(38, 185, 154, 0.7)",
                    pointHoverBackgroundColor: "#fff",
                    pointHoverBorderColor: "rgba(220,220,220,1)",
                    pointBorderWidth: 1,
                    data: []  // Data will be dynamically updated
                }]
            },
        });

        // Initial chart update for the 'Last 7 Days' (default range)
        const start = moment.utc().subtract(6, 'days');  // 7 days ago
        const end = moment.utc();  // Today
        updateProfitLossChart(start, end);
    }
}


function init_daterangepicker() {
    if (typeof ($.fn.daterangepicker) === 'undefined') { return; }
    console.log('init_daterangepicker');

    var cb = function (start, end, label) {
        let displayStart, displayEnd;

        if (label === "Yesterday") {
            displayStart = start.clone().subtract(1, 'days');
            displayEnd = end.clone().subtract(1, 'days');
        } else if (label === "Last 7 Days") {
            displayStart = start.clone().subtract(1, 'days');
            displayEnd = moment().subtract(1, 'days');
        } else if (label === "Last 30 Days") {
            displayStart = start.clone().subtract(1, 'days');
            displayEnd = moment().subtract(1, 'days');
        } else if (label === "Last Month") {
            displayStart = start.clone().subtract(1, 'days');
            displayEnd = moment().subtract(1, 'days');
        } else {
            displayStart = start;
            displayEnd = end;
        }

        // Console display for debugging purposes
        console.log(displayStart.toISOString(), displayEnd.toISOString(), label);

        // Adjust HTML span display
        $('#reportrange span').html(displayStart.format('MMMM D, YYYY') + ' - ' + displayEnd.format('MMMM D, YYYY'));
    };

    var optionSet1 = {
        showDropdowns: true,
        showWeekNumbers: true,
        timePicker: false,
        timePickerIncrement: 1,
        timePicker12Hour: true,
        ranges: {
            // 'Today': [moment(), moment()],
            'Yesterday': [moment(), moment()],
            'Last 7 Days': [moment.utc().subtract(6, 'days'), moment.utc()],
            'Last 30 Days': [moment.utc().subtract(29, 'days'), moment.utc()],
            'This Month': [moment.utc().startOf('month'), moment.utc().endOf('month')],
            'Last Month': [moment.utc().subtract(1,'month').startOf('month').add(1, 'day'), moment.utc().subtract(1,'month').endOf('month').add(1, 'day')]
        },
        // opens: 'left',
        // buttonClasses: ['btn btn-default'],
        // applyClass: 'btn-small btn-primary',
        // cancelClass: 'btn-small',
        // format: 'MM/DD/YYYY',
        // separator: ' to ',
        // locale: {
        //     applyLabel: 'Submit',
        //     cancelLabel: 'Clear',
        //     fromLabel: 'From',
        //     toLabel: 'To',
        //     customRangeLabel: 'Custom',
        //     daysOfWeek: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
        //     monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        //     firstDay: 1
        // }
    };

    $('#reportrange span').html(moment().subtract(29, 'days').format('MMMM D, YYYY') + ' - ' + moment().format('MMMM D, YYYY'));
    $('#reportrange').daterangepicker(optionSet1, cb);

    // When date range is applied, update the chart
    $('#reportrange').on('apply.daterangepicker', function (ev, picker) {
        const startDateUTC = picker.startDate.utc();
        const endDateUTC = picker.endDate.utc();

        // For "Today," adjust to the last 24 hours
        if (picker.chosenLabel === "Today") {
            const last24HoursStart = moment().subtract(24, 'hours').utc();
            updateProfitLossChart(last24HoursStart, endDateUTC, true); // Hourly mode for last 24 hours
        } else {
            updateProfitLossChart(startDateUTC, endDateUTC, false); // Regular range mode
        }
    });
}



$(document).ready(function () {
    $('#menu_toggle').on('click', function () {
        $('body').toggleClass('nav-md nav-sm');
    });

    init_gauge(); // Initialize the Gauge.js when the document is ready
    init_echarts(); // Initialize the ECharts when the document is ready
    init_charts();
    init_daterangepicker();
});


// To-do list
$(document).ready(function () {

    // Show the modal for adding a new task
    $('#addTaskBtn').click(function () {
        $('#taskInput').val('');
        $('#taskId').val('');
        $('#taskModalLabel').text('Add Task');
        $('#taskModal').modal('show');
    });

    // Save or update a task
    $('#saveTaskBtn').click(function () {
        const taskId = $('#taskId').val();
        const task = $('#taskInput').val().trim();
    
        if (!task) {
            alert('Please enter a task description.');
            return;
        }
        
        const requestType = taskId ? 'PUT' : 'POST';
        const url = taskId ? `/api/tasks/${taskId}` : '/api/tasks';
        
        $.ajax({
            url: url,
            method: requestType,
            contentType: 'application/json',
            data: JSON.stringify({ task: task, completed: false }),
            success: function () {
                $('#taskModal').modal('hide');
                location.reload();  // Reload the entire dashboard after adding or updating
            },
            error: function (xhr, status, error) {
                console.error('Error Details:', xhr.responseText);
                alert(`An error occurred while saving the task: ${xhr.responseText}`);
            }
        });
    });
    
    // Load tasks into the to-do list (not needed if reloading page on every change)
    function loadTasks() {
        $('#todoList').empty();
        $.get('/api/tasks', function (tasks) {
            tasks.forEach(task => {
                $('#todoList').append(`
                    <li data-id="${task._id}">
                        <p style="display: flex; align-items: center;">
                            <input type="checkbox" class="flat" ${task.completed ? 'checked' : ''}>
                            ${task.task}
                            <div style="margin-left: auto;">
                                <a href="#" class="editTask" data-id="${task._id}" style="margin-right: 10px;">
                                    <i class="fa fa-pencil-square-o"></i>
                                </a>
                                <a href="#" class="deleteTask" data-id="${task._id}">
                                    <i class="fa fa-trash"></i>
                                </a>
                            </div>
                        </p>
                    </li>
                `);
            });
            
            // Reinitialize iCheck for new checkboxes
            $('input.flat').iCheck({
                checkboxClass: 'icheckbox_flat-green',
                radioClass: 'iradio_flat-green'
            });
        });
    }

    // Edit task
    $(document).on('click', '.editTask', function () {
        const taskId = $(this).data('id');
        const taskText = $(this).closest('p').text().trim();
        $('#taskInput').val(taskText);
        $('#taskId').val(taskId);
        $('#taskModalLabel').text('Edit Task');
        $('#taskModal').modal('show');
    });

    // Delete task
    $(document).on('click', '.deleteTask', function () {
        const taskId = $(this).data('id');
        $.ajax({
            url: `/api/tasks/${taskId}`,
            method: 'DELETE',
            success: function () {
                location.reload();  // Reload the entire dashboard after deleting
            },
            error: function () {
                alert('An error occurred while deleting the task.');
            }
        });
    });
});


//icheck
$(document).ready(function () {
    if ($("input.flat")[0]) {
        $(document).ready(function () {
            $('input.flat').iCheck({
                checkboxClass: 'icheckbox_flat-green',
                radioClass: 'iradio_flat-green'
            });
        });
    }
});

$(document).ready(function () {
    // Initialize progress bars dynamically
    $(".progress .progress-bar").each(function () {
        const progressValue = $(this).data('transitiongoal');
        if (progressValue !== undefined) {
            $(this).css('width', progressValue + '%'); // Set width dynamically
            $(this).attr('aria-valuenow', progressValue); // Update ARIA attributes for accessibility
        }
    });
});
