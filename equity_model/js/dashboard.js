   function render(width,margin) {
        var margin = {top: 20, right: 80, bottom: 30, left: 80},
            width = width-margin.right - margin.left,
            height = 500 - margin.top - margin.bottom;
        var formatDollar = d3.format(",.0f");
        var parseDate = d3.time.format("%Y-%m-%d %I:%M:%S").parse;
        var bisectDate = d3.bisector(function(d) { return d.date; }).left;
        var formatDate = d3.time.format("%d-%b-%Y");
        var x = d3.time.scale()
            .range([0, width]);
        var y = d3.scale.linear()
            .range([height, 0]);
        var y1 = d3.scale.linear()
            .range([175+height, height+75]);
        var y2 = d3.scale.linear()
            .range([300+height, height+200]);
        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");
        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");
        var y1Axis = d3.svg.axis()
            .scale(y1)
            .orient("left");
        var y2Axis = d3.svg.axis()
            .scale(y2)
            .orient("left");
        var line = d3.svg.line()
            .x(function(d) { return x(d.date); })
            .y(function(d) { return y(d.close); });
        var portfolio = d3.svg.line()
            .x(function(d) { return x(d.date); })
            .y(function(d) { return y(d.portfolio); });
        var area = d3.svg.area()
            .x(function(d) { return x(d.date); })
            .y0(height+175)
            .y1(function(d) { return y1(d.portfolioDrawDown);});
        var area2 = d3.svg.area()
            .x(function(d) { return x(d.date); })
            .y0(height+300)
            .y1(function(d) { return y2(d.benchmarkDrawDown);});
        var svg = d3.select("div.col-sm-8").append("svg")
            .attr("width", "100%")
            .attr("height", height + margin.top + margin.bottom + 300)
          .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        var focus = svg.append("g")
            
            .attr("width","100%");
        d3.json("data.php", function(error, data) {
            if (error) throw error;
            data.forEach(function(d) {
                d.date = parseDate(d.date);
                d.close = +d.close;
                d.portfolio = +d.portfolio;
                d.securityNameOne = d.securityNameOne;
                d.securityNameTwo = d.securityNameTwo;
                d.openProfitOne = +d.openProfitOne;
                d.openProfitTwo = +d.openProfitTwo;
                d.portfolioDrawDown = +d.portfolioDrawDown;
                d.benchmarkDrawDown = +d.benchmarkDrawDown;
              });

            x.domain(d3.extent(data, function(d) { return d.date; }));
            y.domain([0, d3.max(data, function(d) { return d.portfolio; })]);
            y1.domain([0, d3.max(data, function(d) { return d.portfolioDrawDown; })]);
            y2.domain([0, d3.max(data, function(d) { return d.benchmarkDrawDown; })]);
            svg.append("path")
                  .datum(data)
                  .attr("class", "line2")
                  .attr("d", line)
                  ;
            svg.append("path")
                  .datum(data)
                  .attr("class", "area")
                  .attr("d", area)
                  ;
            svg.append("path")
                  .datum(data)
                  .attr("class", "area2")
                  .attr("d", area2)
                  ;
            svg.append("path")
                  .datum(data)
                  .attr("class", "line")
                  .attr("d", portfolio)
                  ;

            svg.append("g")
                  .attr("class", "x axis")
                  .attr("transform", "translate(0," + height + ")")
                  .call(xAxis);

            svg.append("g")
                  .attr("class", "y axis")
                  .call(yAxis.tickFormat(d3.format("$,.0f")));
            svg.append("g")
                  .attr("class", "y axis")
                  .call(y2Axis.ticks(6).tickFormat(d3.format(".0%")));
            svg.append("g")
                  .attr("class", "y axis")
                  .call(y1Axis.ticks(6).tickFormat(d3.format(".0%")));
                svg.append("text")
                  .attr("transform", "rotate(-90)")
                  .attr("y", 6)
                  .attr("dy", ".71em")
                  .style("text-anchor", "end")
                  .text("$ Value"); 
            focus.append("circle")
                .attr("class", "y")
                .style("fill", "steelblue")
                .style("stroke", "steelblue")
                .attr("r", 5);
            focus.append("text")
                .attr("class", "y1")
                .style("stroke", "white")
                .style("stroke-width", "3.5px")
                .style("opacity", 0.8)
                .attr("dx", 8)
                .attr("dy", "-.3em");
            focus.append("text")
                .attr("class", "y2")
                .attr("dx", 8)
                .attr("dy", "-.3em");
            focus.append("text")
                .attr("class", "y3")
                .style("stroke", "white")
                .style("stroke-width", "3.5px")
                .style("opacity", 0.8)
                .attr("dx", 8)
                .attr("dy", "1em");
            focus.append("text")
                .attr("class", "y4")
                .attr("dx", 8)
                .attr("dy", "1em");
            focus.append("text")
                .attr("class", "y6")
                .attr("dx", 8)
                .attr("dy", "3em");
            focus.append("text")
                .attr("class", "y7")
                .attr("dx", 8)
                .attr("dy", "4.4em");
            focus.append("text")
                .attr("class", "y8")
                .attr("dx", 8)
                .attr("dy", "38em");
            focus.append("text")
                .attr("class", "y9")
                .attr("dx", 8)
                .attr("dy", "48.5em");
            focus.append("line")
                .attr("class", "x")
                .style("stroke", "steelblue")
                .style("stroke-dasharray", "3,3")
                .style("opacity", 0.5)
                .attr("y1", 0)
                .attr("y2", height);
            svg.append("rect")
                .attr("class","rectMouseover")
                .attr("width", width + "px")
                .attr("height", height +300 + "px")
                .style("fill", "none")
                .style("pointer-events", "all")
                .on("mouseover", function() { focus.style("display", null); })
                .on("mousemove", mousemove);
                var x0 = x.invert(200),
                    i = bisectDate(data, x0, 1),
                    d0 = data[i - 1],
                    d1 = data[i],
                    d = x0 - d0.date > d1.date - x0 ? d1 : d0;
                focus.select("circle.y")
                    .attr("transform","translate(" + x(d.date) + "," +y(d.portfolio) + ")");
                focus.select("text.y2")
                  .attr("transform","translate(50,80)")
                  .text("Portfolio $" + formatDollar(d.portfolio));
                focus.select("text.y6")
                  .attr("transform","translate(50,80)")
                  .text(d.securityNameOne + " Open Profit: $" + formatDollar(d.openProfitOne));
                focus.select("text.y7")
                  .attr("transform","translate(50,80)")
                  .text(d.securityNameTwo + " Open Profit: $" + formatDollar(d.openProfitTwo));
                focus.select("text.y8")
                  .attr("transform","translate(50,80)")
                  .text("Drawdown: " + d3.format(".0%")(d.portfolioDrawDown));
                focus.select("text.y9")
                  .attr("transform","translate(50,80)")
                  .text("Drawdown: " + d3.format(".0%")(d.benchmarkDrawDown));
                focus.select("text.y4")
                    .attr("transform","translate(50,80)")
                    .text(formatDate(d.date));
               
                focus.select(".x")
                    .attr("transform","translate(" + x(d.date) + "," +y(d.portfolio) + ")")
                    .attr("y2", height +300 - y(d.portfolio));
            function mousemove() {  
                var x0 = x.invert(d3.mouse(this)[0]),
                    i = bisectDate(data, x0, 1),
                    d0 = data[i - 1],
                    d1 = data[i],
                    d = x0 - d0.date > d1.date - x0 ? d1 : d0;
                focus.select("circle.y")
                    .attr("transform","translate(" + x(d.date) + "," +y(d.portfolio) + ")");
                focus.select("text.y2")
                  .attr("transform","translate(50,80)")
                  .text("Portfolio $" + formatDollar(d.portfolio));
                focus.select("text.y6")
                  .attr("transform","translate(50,80)")
                  .text(d.securityNameOne + " Open Profit: $" + formatDollar(d.openProfitOne));
                focus.select("text.y7")
                  .attr("transform","translate(50,80)")
                  .text(d.securityNameTwo + " Open Profit: $" + formatDollar(d.openProfitTwo));
                focus.select("text.y8")
                  .attr("transform","translate(50,80)")
                  .text("Drawdown: " + d3.format(".0%")(d.portfolioDrawDown));
                focus.select("text.y9")
                  .attr("transform","translate(50,80)")
                  .text("Drawdown: " + d3.format(".0%")(d.benchmarkDrawDown));
                focus.select("text.y4")
                    .attr("transform","translate(50,80)")
                    .text(formatDate(d.date));
               
                focus.select(".x")
                    .attr("transform","translate(" + x(d.date) + "," +y(d.portfolio) + ")")
                    .attr("y2", height +300 - y(d.portfolio));
                } 
            function resize() {
                var oldFocusX = d3.transform(d3.select("circle.y").attr("transform")).translate[0]
                var x0 = x.invert(oldFocusX),
                    i = bisectDate(data, x0, 1),
                    d0 = data[i - 1],
                    d1 = data[i],
                    d = x0 - d0.date > d1.date - x0 ? d1 : d0;
                var margin = {top: 20, right: 60, bottom: 30, left: 60},
                
                width = parseInt(d3.select("div.col-sm-8").style("width"))-margin.right - margin.left,
                height = 500 - margin.top - margin.bottom;
                x.range([0, width]);
                xAxis.scale(x);
                x.domain(d3.extent(data, function(d) { return d.date; }));
                svg.select('.x.axis')
                  .attr("transform", "translate(0," + height + ")")
                  .call(xAxis);
                svg.select("rect.rectMouseover").attr("width", width + "px");
                line
                    .x(function(d) { return x(d.date); })
                    .y(function(d) { return y(d.close); });
                portfolio
                    .x(function(d) { return x(d.date); })
                    .y(function(d) { return y(d.portfolio); });
                area
                    .x(function(d) { return x(d.date); })
                    .y0(height+175)
                    .y1(function(d) { return y1(d.portfolioDrawDown);});
                area2
                    .x(function(d) { return x(d.date); })
                    .y0(height+300)
                    .y1(function(d) { return y2(d.benchmarkDrawDown);});
                svg.select('.line').attr("d", portfolio);
                svg.select('.line2').attr("d", line);
                svg.select('.area').attr("d", area);
                svg.select('.area2').attr("d", area2);
                focus.select("circle.y")
                    .attr("transform","translate(" + x(d.date) + "," +y(d.portfolio) + ")");
                focus.select(".x")
                    .attr("transform","translate(" + x(d.date) + "," +y(d.portfolio) + ")")
                    .attr("y2", height - y(d.portfolio));
                }
            d3.select(window).on('resize', resize);
        });
        legend = svg.append("g")
            .attr("class","legend")
            .attr("transform","translate(50,30)")
            .style("font-size","12px")
        legend
            .append('rect')
            .attr("class","legendRect")
            .attr('y','0px')
            .attr('x','0px')
            .style("fill","steelblue")
        legend
            .append('text')
            .attr('y','5px')
            .attr('x','10px')
            .text('Portfolio')
        legend
            .append('rect')
            .attr("class","legendRect")
            .style("fill","#707C80")
            .attr('y','15px')
            .attr('x','0px')
            .text('Portfolio')
        legend
            .append('text')
            .attr('y','20px')
            .attr('x','10px')
            .text('Benchmark')

    }

    