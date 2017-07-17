/*
 @param: dataUrl is a URL to a pipe-separated-value file of the form:
   chart|date|executionTime|upstreamLatency|proxyLatency|responseCode
 For example: https://raw.githubusercontent.com/bcgov/dbcrss/master/heartbeat/src/geocoder-public-heartbeat.txt
*/
makeCharts = function(dataUrl) {

  var margin = {
          top: 40,
          right: 50,
          bottom: 40,
          left: 70
      },
      width = 1150 - margin.left - margin.right,
      height = 350 - margin.top - margin.bottom;

  var fractionUpperGraph = 0.75;
  var spaceBetweenUpperAndLower = 25; //px

  var timeoutMs = 60000;

  var upperHeight = height * fractionUpperGraph;
  var lowerHeight = height * (1-fractionUpperGraph) - spaceBetweenUpperAndLower;

  var parseDate = d3.time.format("%H:%M:%S").parse;

  var psv = d3.dsv("|", "text/plain");

  var x = d3.time.scale().range([0, width]);
  var y = d3.scale.linear().range([upperHeight, 0]);
  var y2 = d3.scale.linear().range([upperHeight+spaceBetweenUpperAndLower+lowerHeight, upperHeight+spaceBetweenUpperAndLower+0]);

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
          return y(d.serverSideResponseTimeMs);
      })
      .defined(function(d) { 
        return !isNaN(d.serverSideResponseTimeMs) && d.serverSideResponseTimeMs < timeoutMs;
      })


  var line2 = d3.svg.line()
      .x(function(d) {
          return x(d.date);
      })
      .y(function(d) {
          return y2(d.serverSideFractionExecutionTime);
      })
      .defined(function(d) { 
        return !isNaN(d.serverSideFractionExecutionTime) && d.serverSideResponseTimeMs < timeoutMs && d.serverSideResponseTimeMs > 0;
      })

  /*
  var line3 = d3.svg.line()
      .x(function(d) {
          return x(d.date);
      })
      .y(function(d) {
          return y2(d.proxyLatency);
      });
      */

  // add an X axis line on the bottom of the chart with 24 tick marks (hours of the day)
  var xAxis = d3.svg.axis().scale(x)
      .orient("bottom").ticks(24);

  // add a Y axis line on the left of the chart with tick marks
  var yAxisUpper = d3.svg.axis().scale(y)
      .orient("left").ticks(10)
      .innerTickSize(-width);

  var notTimeout = function(d) {
    if (d.serverSideResponseTimeMs > timeoutMs)
      return null;
    return d.serverSideResponseTimeMs;
  };

  //get the data
  psv(dataUrl, function(error, data) {
      data.forEach(function(d) {
          d.date = parseDate(d.date);
          d.executionTime = +d.executionTime;
          d.upstreamLatency = +d.upstreamLatency;

          //proxy latency and upstream latency described here:
          //https://getkong.org/docs/0.10.x/proxy/
          //upstream latency is essentially the sum of executionTime (of the upstream app) and network latency of sending the response
          //from the upstream app back to kong
          d.networkLatencyBetweenKongAndUpstream = parseFloat(d.upstreamLatency) - d.executionTime;
          d.serverSideResponseTimeMs = parseFloat(d.proxyLatency) + d.networkLatencyBetweenKongAndUpstream + d.executionTime;
          d.serverSideFractionExecutionTime = d.executionTime / d.serverSideResponseTimeMs;
      });

      // Scale the range of the data on the X axis
      x.domain(d3.extent(data, function(d) {
          return d.date;
      }));

      var avgServerSideResponseTimeMs = d3.median(data, notTimeout);
      var avgLine1 = d3.svg.line()
          .x(function(d) { return x(d.date); })
          .y(function(d) { return y(avgServerSideResponseTimeMs); });

      // Scale the range of the data on the Y axis (left)
      //y.domain([0, 100]);
      var maxYAxisVal = d3.max(data, notTimeout);
      if (maxYAxisVal > 10*avgServerSideResponseTimeMs)
        maxYAxisVal = 10*avgServerSideResponseTimeMs;
      
      y.domain([0, maxYAxisVal]);

      // Scale the range of the data on the Y axis (right)
      y2.domain([0, d3.max(data, function(d) {
          return Math.max(d.serverSideFractionExecutionTime);
      })]);

      // add a Y axis line on the right of the chart with tick marks
      var yAxisLower = d3.svg.axis().scale(y2)
          .orient("left").tickValues(y2.domain())
          .innerTickSize(-width);

      // Nest data by chart.
      var charts = d3.nest()
          .key(function(d) {
              return d.chart;
          })
          .sortKeys(d3.descending)
          .entries(data);

      // Compute the maximum serverSideResponseTimeMs per chart, needed for the y-domain.
      charts.forEach(function(s) {
          s.maxServerSideResponseTimeMs = d3.max(s.values, function(d) {
              return d.serverSideResponseTimeMs;
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
      var svg = d3.select("#chart-container").selectAll("svg")
          .data(charts)
          .enter().append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
          .append("g")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      // Add the X Axis (bottom)
      svg.append("g")
          .attr("class", "x axis")
          .attr("y", height - 6)
          .attr("transform", "translate(0," + height + ")")
          .attr("dy", "0.8em")
          .style("font-size", "0.8em")
          .call(xAxis);

      // Label the X Axis
      svg.append("text")
          .attr("transform", "translate(" + (width / 2) + " ," + (height + margin.bottom) + ")")
          .attr("x", -45)
          .style("text-anchor", "middle")
          .text(function(d) {
              return moment(new Date(d.key)).format('MMM. DD YYYY')
          });

      // Add the Y Axis (upper)
      svg.append("g")
          .attr("class", "y axis")
          .style("fill", "blue")
          .style("font-size", "0.8em")
          .call(yAxisUpper);

      //Label the Y axis (upper)
      svg.append("text")
          .attr("transform", "rotate(-90)")
          .attr("x", 0 - (upperHeight / 2))
          .attr("y", -70)
          .attr("dy", "1em")
          .style("font-size", "1em")
          .style("text-anchor", "middle")
          .text("Server-side");
      svg.append("text")
          .attr("transform", "rotate(-90)")
          .attr("x", 0 - (upperHeight / 2))
          .attr("y", -70)
          .attr("dy", "2em")
          .style("font-size", "1em")
          .style("text-anchor", "middle")
          .text("processing time (ms)");

    
      svg.append("rect")
          .attr("width", width)
          .attr("height", lowerHeight)
          .attr("transform", "translate(0,"+(upperHeight+spaceBetweenUpperAndLower)+")")
          .attr("fill", "#eeeeee");

      // Add the Y Axis (lower)
      svg.append("g")
          .attr("class", "y axis")
          //.attr("transform", "translate(" + (width - 10) + " ,0)")
          .style("fill", "red")
          .style("font-size", "0.8em")
          .call(yAxisLower);

      //Label the Y axis (lower)
      svg.append("text")
          .attr("transform", "rotate(-90)")
          .attr("x", 0 - (lowerHeight/ 2) - upperHeight - spaceBetweenUpperAndLower)
          .attr("y", -60)
          .attr("dy", "1em")
          .style("font-size", "1em")
          .style("text-anchor", "middle")
          .text("Fraction");
      svg.append("text")
          .attr("transform", "rotate(-90)")
          .attr("x", 0 - (lowerHeight/ 2) - upperHeight - spaceBetweenUpperAndLower)
          .attr("y", -60)
          .attr("dy", "2em")
          .style("font-size", "1em")
          .style("text-anchor", "middle")
          .text("Execution");

      /*
      // Add the area path elements.
      svg.append("path")
          .attr("class", "area")
          .attr("d", function(d) {
              //y.domain([0, d.maxServerSideResponseTimeMs]);
              return area(d.values);
          });
          */

      // Add the line path elements.
      svg.append("path")
          .attr("class", "line1")
          .attr("d", function(d) {
              //y.domain([0, d.maxServerSideResponseTimeMs]);
              return line(d.values);
          });

      svg.append("path")
          .attr("class", "avg-line1")
          .attr("d", function(d) {
              //y.domain([0, d.maxServerSideResponseTimeMs]);
              return avgLine1(d.values);
          });


      // Add the second line path elements.
      svg.append("path")
          .attr("class", "line2")
          .attr("d", function(d) {
              //y2.domain([0, 1]);
              return line2(d.values);
          });

      /*
      svg.append("path")
          .attr("class", "line3")
          .attr("d", function(d) {
              y.domain([0, d.maxServerSideResponseTimeMs]);
              return line3(d.values);
          });
          */


  });

} //end function