# d3.js Equity Momentum Dashboard

# equity_model

This folder contains the files needs to generate the web based dashboard. Index.php is used to pull in the 'render' function in dashboard.js, which visualizes the output of the equity index backtest. The remainder of the php files in the this folder pull the data from the MySQL database for the tables, last run data, and d3.js dashboard.

#pythonScript

Contains the script that is run each night. The script runs the momentum model by pulling in Yahoo finance pricing data and inserting the results of the backtest into a MySQL database.