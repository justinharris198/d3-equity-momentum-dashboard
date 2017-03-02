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
echo "<h3 align = 'center'>Current Holdings</h3>";
$results = array();
while($row = mysql_fetch_array($retval, MYSQL_ASSOC))
{
  $results[] = $row;

}

  echo "  <table class = 'holdingsTable' cellpadding'0' cellspacing='0' width='100%' border='0'>
            <tr>
              <td class = 'holdingsTd'> </td>
              <td class = 'holdingsTd'>";
  echo $results[0]['securityName'];
  echo "</td>
              <td class = 'holdingsTd'>"; 
  echo $results[1]['securityName'];
  echo "</td>
            </tr>
            <tr>
              <td>Yahoo Code: </td>
              <td>"; 
  echo $results[0]['security'];
  echo "</td>
              <td> ";
  echo $results[1]['security'];
  echo "</td>
            </tr>
            <tr>
              <td>Shares: </td>
              <td> ";
  echo $results[0]['shares'];
  echo "</td>
              <td> ";
  echo $results[1]['shares'];
  echo "</td>
            </tr>
            <tr>
              <td>PnL: </td>
              <td> ";
  echo "$".round((float)$results[0]['unrealizedPAndL']);
  echo "</td>
              <td> ";
  echo "$".round((float)$results[1]['unrealizedPAndL']);
  echo "</td>
            </tr>

          </table>";
   
   mysql_close($conn);
?>
