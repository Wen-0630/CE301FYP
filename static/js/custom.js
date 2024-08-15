$(document).ready(function () {
    $('#menu_toggle').on('click', function () {
        $('body').toggleClass('nav-md nav-sm');
    });
});

var chart_gauge_01;

function init_gauge() {
    if (typeof (Gauge) === 'undefined') { 
        console.log('Gauge.js library not found!');
        return; 
    }

    console.log('init_gauge [' + $('.gauge-chart').length + ']');

    var chart_gauge_settings = {
        lines: 12, 
        angle: 0, // Angle of the gauge arc (0.15 for a semicircle gauge)
        lineWidth: 0.4, // Width of the gauge arc
        pointer: {
            length: 0.75, 
            strokeWidth: 0.042, 
            color: '#1D212A' 
        },
        limitMax: true, // Enable max value limit
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

            // Calculate the relative value for the gauge
            var relativeValue = (currentValue / maxValue) * maxValue;
            chart_gauge_01.set(relativeValue); 

            // If you want to set a text field, you can set it here
            // chart_gauge_01.setTextField(document.getElementById("gauge-text")); 
        } else {
            console.error('Invalid values for max or current value.');
        }
    }
}

$(document).ready(function () {
    $('#menu_toggle').on('click', function () {
        $('body').toggleClass('nav-md nav-sm');
    });

    init_gauge(); // Initialize the gauge when the document is ready
});
