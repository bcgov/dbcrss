var margin = {
        top: 55,
        right: 50,
        bottom: 40,
        left: 50
    },
    width = 1250 - margin.left - margin.right,
    height = 350 - margin.top - margin.bottom;

var parseDate = d3.time.format("%H:%M:%S").parse;

var psv = d3.dsv("|", "text/plain");

var x = d3.time.scale().range([0, width]);
var y = d3.scale.linear().range([height, 0]);

var y2 = d3.scale.linear().range([height, 0]);

var area = d3.svg.area()
    .x(function(d) {
        return x(d.date);
    })
    .y0(height)
    .y1(function(d) {
        return y(d.executionTime);
    });

var line = d3.svg.line()
    .x(function(d) {
        return x(d.date);
    })
    .y(function(d) {
        return y(d.executionTime);
    });

var line2 = d3.svg.line()
    .x(function(d) {
        return x(d.date);
    })
    .y(function(d) {
        return y2(d.upstreamLatency);
    });

var line3 = d3.svg.line()
    .x(function(d) {
        return x(d.date);
    })
    .y(function(d) {
        return y2(d.proxyLatency);
    });

// add an X axis line on the bottom of the chart with 24 tick marks (hours of the day)
var xAxis = d3.svg.axis().scale(x)
    .orient("bottom").ticks(24);

// add a Y axis line on the left of the chart with tick marks
var yAxis = d3.svg.axis().scale(y)
    .orient("left").ticks(10)
    .innerTickSize(-width);

// add a Y axis line on the right of the chart with tick marks
var yAxisRight = d3.svg.axis().scale(y2)
    .orient("right").ticks(10);
//.innerTickSize(-width);

//get the data
psv("https://raw.githubusercontent.com/bcgov/dbcrss/master/heartbeat/src/test.txt", function(error, data) {
    data.forEach(function(d) {
        d.date = parseDate(d.date);
        d.executionTime = +d.executionTime;
        d.upstreamLatency = +d.upstreamLatency;
    });

    // Scale the range of the data on the X axis
    x.domain(d3.extent(data, function(d) {
        return d.date;
    }));

    // Scale the range of the data on the Y axis (left)
    //y.domain([0, 100]);
    y.domain([0, d3.max(data, function(d) {
        return Math.max(d.executionTime);
    })]);

    // Scale the range of the data on the Y axis (right)
    y2.domain([0, d3.max(data, function(d) {
        return Math.max(d.upstreamLatency);
    })]);

    // Nest data by chart.
    var charts = d3.nest()
        .key(function(d) {
            return d.chart;
        })
        .entries(data);

    // Compute the maximum executionTime per chart, needed for the y-domain.
    charts.forEach(function(s) {
        s.maxexecutionTime = d3.max(s.values, function(d) {
            return d.executionTime;
        });
    });

    // Calculate the minimum and maximum date across charts.
    x.domain([
        d3.min(charts, function(s) {
            return s.values[0].date;
        }),
        d3.max(charts, function(s) {
            return s.values[s.values.length - 1].date;
        })
    ]);

    // Add an svg element for each chart
    var svg = d3.select("body").selectAll("svg")
        .data(charts)
        .enter().append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Add the area path elements.
    svg.append("path")
        .attr("class", "area")
        .attr("d", function(d) {
            y.domain([0, d.maxexecutionTime]);
            return area(d.values);
        });

    // Add the line path elements.
    svg.append("path")
        .attr("class", "line")
        .attr("d", function(d) {
            y.domain([0, d.maxexecutionTime]);
            return line(d.values);
        });

    // Add the second line path elements.
    svg.append("path")
        .attr("class", "line2")
        .attr("d", function(d) {
            y.domain([0, d.maxexecutionTime]);
            return line2(d.values);
        });

    svg.append("path")
        .attr("class", "line3")
        .attr("d", function(d) {
            y.domain([0, d.maxexecutionTime]);
            return line3(d.values);
        });

    svg.append("g")
        .attr("class", "x axis")
        .attr("y", height - 6)
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // Add the Y Axis
    svg.append("g")
        .attr("class", "y axis")
        .style("fill", "blue")
        .call(yAxis);

    svg.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + (width - 10) + " ,0)")
        .style("fill", "red")
        .call(yAxisRight);

    // Add the text label for the x axis
    svg.append("text")
        .attr("transform", "translate(" + (width / 2) + " ," + (height + margin.bottom) + ")")
        .attr("x", -45)
        .style("text-anchor", "middle")
        .text(function(d) {
            return d.key;
        });

    //Label the Y axis (left side)
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", 0 - (height / 2))
        .attr("y", -49)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Milliseconds");

    //Label the Y axis (right side)
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", 0 - (height / 2))
        .attr("y", +1175)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Milliseconds");

});
