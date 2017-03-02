<?php
   $dbhost = '';
   $dbuser = '';
   $dbpass = '';
   
   $conn = mysql_connect($dbhost, $dbuser, $dbpass);
   
   if(! $conn ) {
      die('Could not connect: ' . mysql_error());
   }
   
   $sql = 'select distinct lastRunDate from equityModelportfolioMetrics';
   mysql_select_db('analytics');
   $retval = mysql_query( $sql, $conn );

while($row = mysql_fetch_array($retval, MYSQL_ASSOC))
{
  $lastRunDate = date_format(date_create($row['lastRunDate']),"m/d/Y");
  echo "$lastRunDate";
  

}

   
   mysql_close($conn);
?>