<!DOCTYPE html>
<meta charset="utf-8">
<link rel="stylesheet" href="css/bootstrap.css">
<style>

body {
  font: 12px sans-serif;
}
table.holdingsTable tr td { width:25%; padding-top:5px;font-size:12px; }
tr:first-child {font-weight:bold;padding-bottom:5px;}
h4 {
    background-color: steelblue;
    color:white;
    padding-top:20px;
    padding-bottom:20px;
    padding-right:10px;
    padding-left:10px;
}
h6 {line-height:1.5;}
.axis path,
.axis line {
  fill: none;
  stroke: #000;
  shape-rendering: crispEdges;
}
.area {
    fill: steelblue ;
  stroke-width: 1.5px;
}
.area2 {
    fill: #707C80;
  stroke-width: 1.5px;
}
.line {
    fill: none;
  stroke: steelblue ;
  stroke-width: 1.5px;
}
.line2 {
    fill: none;
  stroke: #707C80;
  stroke-width: 1.5px;
}
.portfolioMetrics {
    font-size:10px;
    font-weight: bold
}
.tdCenter {
    padding-right:10px;
    padding-left:10px;
    text-align:center;

}
.tdLeft {
    padding-right:10px;
    padding-left:0px;
    text-align:left;}
.legend {height:100px;width:100px;}
.legendRect {width:5px; height:5px; }
#portfolioStatistics {margin-left:5%;width:35%;float:left;}
#currentHoldings {margin-left:5%;width:35%;float:left}
</style>
<body>
<script src="http://d3js.org/d3.v3.min.js"></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
<script src="js/dashboard.js"></script>
<div class = "container">
<div class = "col-sm-12" style="text-align:center">
<h1>Momentum Investment Model</h1></div>
<div class = "col-sm-8">
</div>
<script>
    var width = parseInt(d3.select("div.col-sm-8").style("width"))
    var margin = 0
    render(width,margin);
</script>
<div class = "col-sm-4">
<h6><i>Last Updated - <?php require('currentDate.php') ?>, this algorithmic model shows what returns would have been if an investor shifted allocation globally to the 2 markets (50% portfolio allocation each) with the greatest momentum, measured as the 2 markets with the largest gap between the current price and the 120 day moving average. Trades are made quarterly, or if a stop loss is breached. A stop loss is set on the portfolio level. Both positions are liquidated if the portfolio falls 6% from it's value at the start of the quarter. If 5 markets are not trending up (defined as price above the 120 day moving average), the model stays in 100% cash. (Disclosure: This backtest is for modeling purposes only and does not constitute a recommendation to invest.)</i></h6></div>
<div class = "col-sm-4"><?php require('currentHoldings.php') ?></div>
<div class = "col-sm-4"><?php require('portfolioMetrics.php') ?></div>
</div>
<script>
$('#container').css('width', width);
$('#container').css('margin-left', margin);
$('#container').css('margin-right', margin);
</script>
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-29519117-1', 'auto');
  ga('send', 'pageview');
</script>
</body>