<?php
   $dbhost = '';
   $dbuser = '';
   $dbpass = '';
   
   $conn = mysql_connect($dbhost, $dbuser, $dbpass);
   
   if(! $conn ) {
      die('Could not connect: ' . mysql_error());
   }
   
   $sql = 'select * from equityModelportfolioMetrics';
   mysql_select_db('analytics');
   $retval = mysql_query( $sql, $conn );
echo "<h3 align = 'center'>Portfolio Metrics</h3>";
$results = array();
while($row = mysql_fetch_array($retval, MYSQL_ASSOC))
{
  $results[] = $row;

}

  echo "  <table class = 'holdingsTable' cellpadding'0' cellspacing='0' width='100%' border='0'>
            <tr>
              <td class = 'holdingsTd'> </td>
              <td class = 'holdingsTd'>";
  echo $results[0]['portfolio'];
  echo "</td>
              <td class = 'holdingsTd'>"; 
  echo $results[1]['portfolio'];
  echo "</td>
            </tr>
            <tr>
              <td>Standard Deviation </td>
              <td>"; 
  echo round((float)$results[0]['std'] * 100 ) . '%';
  echo "</td>
              <td> ";
  echo round((float)$results[1]['std'] * 100 ) . '%';
  echo "</td>
            </tr>
            <tr>
              <td>Annualized Return: </td>
              <td> ";
  echo round((float)$results[0]['cumulativeReturn'] * 100 ) . '%';
  echo "</td>
              <td> ";
  echo round((float)$results[1]['cumulativeReturn'] * 100 ) . '%';
  echo "</td>
            </tr>
            <tr>
              <td>Max Drawdown: </td>
              <td> ";
  echo round((float)$results[0]['maxDrawdown'] * 100 ) . '%';
  echo "</td>
              <td> ";
  echo round((float)$results[1]['maxDrawdown'] * 100 ) . '%';
  echo "</td>
            </tr>
            <tr>
              <td>Information Ratio: </td>
              <td> ";
  echo round((float)$results[0]['ir'],2 );
  echo "</td>
              <td> ";
  echo round((float)$results[1]['ir'],2 );
  echo "</td>
            </tr>
          </table>";
   
   mysql_close($conn);
?>










