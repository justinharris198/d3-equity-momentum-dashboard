<?php
   $dbhost = '';
   $dbuser = '';
   $dbpass = '';
   
   $conn = mysql_connect($dbhost, $dbuser, $dbpass);
   
   if(! $conn ) {
      die('Could not connect: ' . mysql_error());
   }
   
   $sql = "select 
  cr.Date AS date, 
  cr.benchmarkPortfolio AS close, 
  cr.portfolio AS portfolio,
case when securityNameOne is null then 'No Holding' else securityNameOne end as securityNameOne,
case when securityNameTwo is null then 'No Holding' else securityNameTwo end as securityNameTwo,
openProfitOne,
openProfitTwo,
abs(portfolioDrawDown) as portfolioDrawDown,
abs(benchmarkDrawDown) as benchmarkDrawDown
from
equityModelCumulativeReturns cr
join equityModelLineDailyHoldings dh on dh.date = cr.date";
   mysql_select_db('analytics');
   $retval = mysql_query( $sql, $conn );
   
   if(! $retval ) {
      die('Could not get data: ' . mysql_error());
   }
   $data = array();
   for ($x = 0; $x < mysql_num_rows($retval); $x++) {
        $data[] = mysql_fetch_assoc($retval);
    }
    
   echo json_encode($data); 
   
   mysql_close($conn);
?>
