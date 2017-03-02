<?php
   $dbhost = '';
   $dbuser = '';
   $dbpass = '';
   
   $conn = mysql_connect($dbhost, $dbuser, $dbpass);
   
   if(! $conn ) {
      die('Could not connect: ' . mysql_error());
   }
   
   $sql = 'select *, shares * ( previousClose - tradePrice ) AS unrealizedPAndL FROM equityModelDailyHoldings WHERE DATE = ( SELECT MAX( DATE ) FROM equityModelCumulativeReturns )';
   mysql_select_db('analytics');
   $retval = mysql_query( $sql, $conn );
$Description = array();

while($row = mysql_fetch_array($retval, MYSQL_ASSOC))
{
   $Description[] = $row;
}
echo $Description[0]["index"];