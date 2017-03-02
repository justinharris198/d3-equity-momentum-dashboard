import pandas as pd
import quandl
import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.dates as mdates
import datetime
#import xlsxwriter as xl
import pandas_datareader.data as web
import MySQLdb
from pandas.io import sql
import sqlalchemy as sa

'''def visualize_analysis_pyplot(x_return,y_return,benchmarkReturn):
    plt.figure(figsize=(12,8))
    plt.ylabel('Portfolio Value',fontsize=16)
    plt.xlabel('Date',fontsize=16)
    plt.plot(x_return,y_return,linewidth=4)
    plt.plot(x_return,benchmarkReturn,linewidth=4)
    plt.suptitle('Cumulative Returns', fontsize=32)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5,maxticks=10))
    plt.gcf().autofmt_xdate()
    plt.show()'''
class portfolio:
    def __init__(self,firstDate,startingValue):
        self.dailyHoldings = dict()
        self.portfolioValue = startingValue
        self.dailyPAndL = pd.DataFrame({'dayPAndL':0},index=[firstDate])
        self.currentPortfolio = []
        self.dailyHoldingsInsert = []
        self.closedPortfolio = []
        self.equityCurve = pd.DataFrame({'portfolio':self.portfolioValue,'holdings':0.0},index=[firstDate])
    def profitAndLoss(self,currentPortfolio,marketData,marketDate,closedPortfolio):
        self.dailyHoldingsInsert = []
        dayPAndL = 0.0
        for i in currentPortfolio:
            tickerDataFrame = pd.DataFrame(marketData[i[0]][:marketDate])
            tickerDataFrame = tickerDataFrame.dropna(how='any')
            if marketDate == i[3]:
                positionPAndL = ((tickerDataFrame['Close'][-1] - i[1]) * i[2]) - (.001*i[2]*i[1])
            elif marketDate == tickerDataFrame.index[-1]:
                positionPAndL = (tickerDataFrame['Close'][-1] - tickerDataFrame['Close'][-2]) * i[2]
            else:
                positionPAndL = 0.0
            dayPAndL += positionPAndL
            dailyHoldingsInsert = [i[0],i[1],i[2],tickerDataFrame['Close'][-2],tickerDataFrame['Close'][-1],positionPAndL,i[4],i[5],i[6]]
            self.dailyHoldingsInsert.append(dailyHoldingsInsert)
        for i in closedPortfolio:
            tickerDataFrame = pd.DataFrame(marketData[i[0]][:marketDate])
            tickerDataFrame = tickerDataFrame.dropna(how='any')
            if marketDate == i[3]:
                positionPAndL = (((tickerDataFrame['Open'][-1] - tickerDataFrame['Close'][-2]) * i[2] ) * (-1)) + .001*i[2]*tickerDataFrame['Open'][-1]
            dayPAndL += positionPAndL
            
        self.dailyHoldings[marketDate] = self.dailyHoldingsInsert
        return dayPAndL
    def portfolioValueUpdate(self,portfolioValue,totalProfitAndLoss):
        return portfolioValue + totalProfitAndLoss
    def currentHoldingsValue(self,marketData,currentPortfolio,marketDate,openClose):
        currentPortfolioValue = 0.0
        for i in currentPortfolio:
            if openClose == 1:
                lastPrice = marketData[i[0],marketDate]['Open']
                if np.isnan(lastPrice):
                    lastPrice = marketData[i[0]][:marketDate].dropna(how='any')[-2:-1]['Close'][0]
            elif openClose == 0:
                lastPrice = marketData[i[0],marketDate]['Close']
                if np.isnan(lastPrice):
                    lastPrice = marketData[i[0]][:marketDate].dropna(how='any')[-2:-1]['Close'][0]
            holdingValue = lastPrice * i[2]
            currentPortfolioValue += holdingValue
        return currentPortfolioValue
class model:
    def __init__(self,countries,country_weights):
        self.dailyRankings = dict()
        self.recommendations = []
        self.weightedGDP = self.gdpData(countries,country_weights)
    def gdpData(self,countries,country_weights):
        gdpDf = pd.DataFrame({'Value':[],'country_code':[]})
        for i in countries:
            gdp = quandl.get("WWDI/"+i+"_NY_GDP_MKTP_KN", authtoken='')
            gdp['country_code'] = i
            gdpDf = gdpDf.append(gdp)
        gdpDf['Date']=gdpDf.index
        weightedGDP = pd.merge(gdpDf, country_weights, how='inner', on='country_code')
        weightedGDP['dollar'] = weightedGDP['allocation']*weightedGDP['Value']
        weightedGDP=weightedGDP.groupby(['ticker', 'Date'])['dollar'].sum()
        return weightedGDP
    def initiatePositionSignal(self,endDate,timeSeriesPanel,weightedGDP):
        analysis = []
        analysisDataFrame = pd.DataFrame({'ticker':[],'gdpPercentile':[],'gdpYoyDelta':[],'meanPriceToGdp':[],'currentStdPriceToGdp':[],'gdpGrowth':[],'aboveMA':[],'monthReturn':[]})
        for i in timeSeriesPanel.axes[0]:
            tickerDataFrame = pd.DataFrame(timeSeriesPanel[i][:endDate])
            tickerDataFrame = tickerDataFrame.dropna(how='any')
            tickerDataFrame['movingAverage'] = tickerDataFrame.Close.rolling(window=120).mean()
            tickerDataFrame['movingAverage20'] = tickerDataFrame.Close.rolling(window=40).mean()
            if len(tickerDataFrame.index) > 756 and tickerDataFrame.Close.iloc[-1] > tickerDataFrame.movingAverage.iloc[-1] and tickerDataFrame.Close.iloc[-1] > tickerDataFrame.movingAverage20.iloc[-1]:
                gdpPercentile = pd.DataFrame(weightedGDP[i])
                gdpPercentile['yoyDelta'] = (gdpPercentile.dollar / gdpPercentile.dollar.shift(1))-1
                gdpPercentile['year'] = gdpPercentile.index.year + 1
                tickerDataFrame['year'] = tickerDataFrame.index.year
                tickerDataFrame['monthReturn'] = tickerDataFrame.Close.iloc[-1] / tickerDataFrame.Close.iloc[-61] - 1
                tickerDataFrame['aboveMA'] = tickerDataFrame.Close.iloc[-1] / tickerDataFrame.movingAverage.iloc[-1] - 1
                tickerDataFrame = pd.merge(gdpPercentile, tickerDataFrame, how='inner', on='year')
                tickerDataFrame['closeToDollar'] = tickerDataFrame.Close / tickerDataFrame.dollar
                tickerDataFrame['rollMean'] = tickerDataFrame.closeToDollar.expanding(min_periods=1).mean()
                tickerDataFrame['rollStd'] = tickerDataFrame.closeToDollar.expanding(min_periods=1).std()
                gdpPercentile = (tickerDataFrame['closeToDollar'].iloc[-1] - tickerDataFrame['rollMean'].iloc[-1]) / tickerDataFrame['rollStd'].iloc[-1]
                analysisDataFrame = analysisDataFrame.append(pd.DataFrame({'ticker':i,'gdpPercentile':gdpPercentile,'gdpYoyDelta':tickerDataFrame['yoyDelta'].iloc[-1],'meanPriceToGdp':tickerDataFrame['rollMean'].iloc[-1],'currentStdPriceToGdp':gdpPercentile,'gdpGrowth':1 if tickerDataFrame['yoyDelta'].iloc[-1] > 0 else 0,'aboveMA':tickerDataFrame['aboveMA'].iloc[-1],'monthReturn':tickerDataFrame['monthReturn'].iloc[-1]},index = [0]))
        if len(analysisDataFrame) > 4:
            analysisDataFrame['maRank'] = analysisDataFrame['aboveMA'].rank(axis=0,ascending=False)
            analysisDataFrame['monthReturnRank'] = analysisDataFrame['monthReturn'].rank(axis=0,ascending=False)
            analysisDataFrame['TotalRank'] = analysisDataFrame['maRank'] + analysisDataFrame['monthReturnRank']
            analysisDataFrame = analysisDataFrame.sort_values('maRank',ascending=True)
            analysisDataFrame = analysisDataFrame[0:2]
            for j in range(len(analysisDataFrame.index)):
                analysis.append([analysisDataFrame['ticker'].iloc[j],1,analysisDataFrame['gdpYoyDelta'].iloc[j],analysisDataFrame['meanPriceToGdp'].iloc[j],analysisDataFrame['currentStdPriceToGdp'].iloc[j]])
        return analysis
    def closePositionSignal(self,endDate,timeSeriesPanel,currentPortfolio):
        analysis = []
        for i in currentPortfolio:
            analysis.append([i[0],1])
        return analysis
class trader:
    def __init__(self,minSize,maxSize):
        self.orders = []
        self.closingOrders = []
        self.portfolioCloseTest = []
        self.tradeLog = dict()
        self.dailyTradeLog = []
        self.minSize = minSize
        self.maxSize = maxSize
    def positionSizer(self,cashAvailableToTrade,numberOfOrders,portfolioValue,minSize,maxSize):
        minDollar = minSize * portfolioValue
        maxDollar = maxSize * portfolioValue
        size = np.minimum(maxDollar,(cashAvailableToTrade / numberOfOrders) * .9985)
        if size < minDollar:
            return 0.0
        else:
            return size
    def orderExecute(self,marketDate,marketData,portfolioValue,order,currentPortfolio,holdingsValue):
        tradesMade = []
        cashAvailableToTrade = portfolioValue - holdingsValue
        dollarSize = self.positionSizer(cashAvailableToTrade,len(order),portfolioValue,self.minSize,self.maxSize)
        ordersNotMade = []
        for order in order:
            try:
                tradePrice = marketData.timeSeriesPanel[order[0],marketDate]['Open']
                sharesTraded = int(dollarSize / tradePrice) * order[1]
                if not np.isnan(tradePrice):                
                    tradesMade.append([order[0],tradePrice,sharesTraded,marketDate,order[2],order[3],order[4]])
                else:
                    ordersNotMade.append(order)
            except:
                ordersNotMade.append(order)
        self.orders = ordersNotMade
        return tradesMade
    def orderExecuteClose(self,marketDate,marketData,portfolioValue,order,currentPortfolio):
        tradesMade = []
        ordersNotMade = []
        for order in order:
            try:
                tradePrice = marketData.timeSeriesPanel[order[0],marketDate]['Open']
                value = [i for i,x in enumerate(currentPortfolio) if x[0] == order[0]]
                sharesTraded = currentPortfolio[value[0]][2] * -1
                if not np.isnan(tradePrice):
                    tradesMade.append([order[0],tradePrice,sharesTraded,marketDate])
                else:
                    ordersNotMade.append(order)
            except:
                ordersNotMade.append(order)
        self.closingOrders = ordersNotMade
        return tradesMade
class marketData:
    def __init__(self,tickerList,source):
        self.toPanelDict = {}
        self.tickerList = tickerList
        if source == 'pd-datareader':
            for i in self.tickerList:
                try:
                    timeSeries = web.DataReader(i, 'yahoo', datetime.date(2000,07,01), datetime.datetime.now().date())
                    timeSeries = self.dataTransformYahoo(timeSeries)
                    timeSeries = self.dataQuality(timeSeries)
                    self.toPanelDict[i] = timeSeries
                except:
                    print i
        if source == 'quandl':
            for i in self.tickerList:
                print i
                timeSeries = quandl.get(i, authtoken='',trim_start = datetime.date(2000,07,01))
                timeSeries = self.dataTransformGoog(timeSeries)
                timeSeries = self.dataQuality(timeSeries)
                self.toPanelDict[i] = timeSeries
        self.timeSeriesPanel=pd.Panel(self.toPanelDict)
    def dataTransformYahoo(self,timeSeries):
        timeSeries['Open'] = timeSeries['Open'] - (timeSeries['Close'] - timeSeries['Adj Close'])
        timeSeries['High'] = timeSeries['High'] - (timeSeries['Close'] - timeSeries['Adj Close'])
        timeSeries['Low'] = timeSeries['Low'] - (timeSeries['Close'] - timeSeries['Adj Close'])
        timeSeries['Close'] = timeSeries['Adj Close']
        return timeSeries
    def dataTransformGoog(self,timeSeries):
        timeSeries['Open'] = timeSeries['Open'].where((timeSeries['Open'] > 0),timeSeries['Close'])
        return timeSeries[['Open','High','Low','Close']]
    def dataQuality(self,timeSeries):
        timeSeries['pctChangeDay'] = timeSeries['Close'] / timeSeries['Close'].shift(1) - 1
        timeSeries['ReturnOpen'] = abs(timeSeries['Open']/timeSeries['Close']-1)
        timeSeries['Open'] = timeSeries['Open'].where((timeSeries['ReturnOpen'] < 0.4),timeSeries['Close'])
        timeSeries = timeSeries[(timeSeries.pctChangeDay < .5) & (timeSeries.pctChangeDay > -.5)][['Open','High','Low','Close']]
        return timeSeries
class backtester:
    def __init__(self,tickerList,startingValue,minSize,maxSize,country_weights,countries):
        self.model = model(countries,country_weights)
        self.trader = trader(minSize,maxSize)        
        self.marketData = marketData(tickerList,'pd-datareader')
        self.portfolio = portfolio(self.marketData.timeSeriesPanel.axes[1][0],startingValue)
    def startBacktest(self,backTestOffset):
        marketDateMonthPrev = 0
        currentValue = self.portfolio.portfolioValue
        for marketDate in self.marketData.timeSeriesPanel.axes[1][backTestOffset:]:
            self.trader.dailyTradeLog = []            
            if len(self.trader.closingOrders) > 0:
                portfolioClose = self.trader.orderExecuteClose(marketDate,self.marketData,self.portfolio.portfolioValue,self.trader.closingOrders,self.portfolio.currentPortfolio)
                self.trader.portfolioCloseTest = portfolioClose
                if len(portfolioClose) > 0:
                    for i in portfolioClose:
                        value = [j for j,x in enumerate(self.portfolio.currentPortfolio) if i[0] == x[0]]
                        self.portfolio.currentPortfolio.remove(self.portfolio.currentPortfolio[value[0]])
                        self.portfolio.closedPortfolio.append(i)
                        self.trader.dailyTradeLog.append(i)
            if len(self.trader.orders) > 0:
                holdingsValue = self.portfolio.currentHoldingsValue(self.marketData.timeSeriesPanel,self.portfolio.currentPortfolio,marketDate,1)
                portfolioInitiate = self.trader.orderExecute(marketDate,self.marketData,self.portfolio.portfolioValue,self.trader.orders,self.portfolio.currentPortfolio,holdingsValue)
                if len(portfolioInitiate) > 0:
                    for i in portfolioInitiate:
                        self.portfolio.currentPortfolio.append(i)
                        self.trader.dailyTradeLog.append(i)
            if len(self.trader.dailyTradeLog) > 0:
                self.trader.tradeLog[marketDate] = self.trader.dailyTradeLog
            if (marketDate.month <> marketDateMonthPrev and (marketDate.month == 3 or marketDate.month == 6 or marketDate.month == 9 or marketDate.month == 12)) or self.portfolio.portfolioValue / currentValue - 1 < -.06:
                currentValue = self.portfolio.portfolioValue
                toInitiate = self.model.initiatePositionSignal(marketDate,self.marketData.timeSeriesPanel,self.model.weightedGDP)
                self.model.recommendations.append([marketDate,toInitiate])
                toClose = self.model.closePositionSignal(marketDate,self.marketData.timeSeriesPanel,self.portfolio.currentPortfolio)
                self.trader.closingOrders = toClose
                self.trader.orders = toInitiate
            dayPAndL = self.portfolio.profitAndLoss(self.portfolio.currentPortfolio,self.marketData.timeSeriesPanel,marketDate,self.portfolio.closedPortfolio)
            self.portfolio.dailyPAndL = self.portfolio.dailyPAndL.append(pd.DataFrame({'dayPAndL':dayPAndL},index=[marketDate]))
            self.portfolio.closedPortfolio = []
            self.portfolio.portfolioValue = self.portfolio.portfolioValueUpdate(self.portfolio.portfolioValue,dayPAndL)
            holdingsValue = self.portfolio.currentHoldingsValue(self.marketData.timeSeriesPanel,self.portfolio.currentPortfolio,marketDate,0)
            self.portfolio.equityCurve = self.portfolio.equityCurve.append(pd.DataFrame({'portfolio':self.portfolio.portfolioValue,'holdings':holdingsValue},index=[marketDate])) 
            marketDateMonthPrev = marketDate.month
backTestStartOffset = 252
startingValue = 1000000
country_weights = pd.read_csv('/var/www/html/pythonScripts/country_indices.csv')
countries = country_weights.country_code.unique()
tickerList = country_weights.ticker.unique()
bbc = backtester(tickerList,startingValue,.03,1,country_weights,countries)
bbc.startBacktest(backTestStartOffset)
dailyHoldings = pd.DataFrame(columns = ['date','security','securityName','tradePrice', 'shares', 'previousClose','close','dayPAndL' ])

for date in sorted(sorted(bbc.portfolio.dailyHoldings)):
    for j in bbc.portfolio.dailyHoldings[date]:
        a = {'date':date,'security':j[0],'securityName':country_weights.loc[country_weights.ticker == j[0],'type'].iloc[0],'tradePrice':j[1], 'shares':j[2], 'previousClose':j[3],'close':j[4],'dayPAndL':j[5], 'gdpYoyDelta':j[6],'meanPriceToGdp':j[7],'currentStd':j[8]}
        dailyHoldings = dailyHoldings.append(a,ignore_index = True)
dateRange = bbc.portfolio.equityCurve[bbc.portfolio.equityCurve.portfolio != 1000000].portfolio.index
portfolioValue = bbc.portfolio.equityCurve[bbc.portfolio.equityCurve.portfolio != 1000000].portfolio
benchmark = timeSeries = bbc.marketData.timeSeriesPanel['^GSPC']
benchmark = timeSeries['Close'] / timeSeries['Close'].shift(1)
benchmark = benchmark[dateRange[0]:dateRange[-1]]
benchmark = benchmark.fillna(1)
benchmark = benchmark.cumprod() * 1000000
attritubtionDataTable = pd.concat([portfolioValue,benchmark],axis=1,join="inner")
attritubtionDataTable.columns = [['portfolio','benchmarkPortfolio']]
attritubtionDataTable['portfolioDrawDown'] = (attritubtionDataTable.portfolio / attritubtionDataTable.portfolio.cummax() - 1)
attritubtionDataTable['benchmarkDrawDown'] = (attritubtionDataTable.benchmarkPortfolio / attritubtionDataTable.benchmarkPortfolio.cummax() - 1)




attritubtionDataTable['portfolioDailyReturns'] = (attritubtionDataTable.portfolio / attritubtionDataTable.portfolio.shift(1) - 1)
attritubtionDataTable['benchmarkDailyReturns'] = (attritubtionDataTable.benchmarkPortfolio / attritubtionDataTable.benchmarkPortfolio.shift(1) - 1)
portfolioStd = attritubtionDataTable['portfolioDailyReturns'][attritubtionDataTable.portfolioDailyReturns!=0].std()*(252**.5)
benchmarkStd = attritubtionDataTable['benchmarkDailyReturns'].std()*(252**.5)
portfolioCumulativeReturn = (attritubtionDataTable.portfolioDailyReturns + 1).prod() ** (365.0 / (attritubtionDataTable.index[-1] - attritubtionDataTable.index[1]).days) - 1
benchmarkCumulativeReturn = (attritubtionDataTable.benchmarkDailyReturns + 1).prod() ** (365.0 / (attritubtionDataTable.index[-1] - attritubtionDataTable.index[1]).days) - 1
portfolioMaxDrawDown = (attritubtionDataTable.portfolio / attritubtionDataTable.portfolio.cummax() - 1).min()
benchmarkMaxDrawDown = (attritubtionDataTable.benchmarkPortfolio / attritubtionDataTable.benchmarkPortfolio.cummax() - 1).min()
ir = (portfolioCumulativeReturn - benchmarkCumulativeReturn) / ((attritubtionDataTable.portfolioDailyReturns - attritubtionDataTable.benchmarkDailyReturns).std()*(252.0**.5))

portfolioMetrics = pd.DataFrame(columns = ['portfolio','std','cumulativeReturn','maxDrawdown', 'ir'])
portfolioMetrics = portfolioMetrics.append({'portfolio':'Portfolio','std':portfolioStd,'cumulativeReturn':portfolioCumulativeReturn,'maxDrawdown':portfolioMaxDrawDown, 'ir':ir},ignore_index=True)
portfolioMetrics = portfolioMetrics.append({'portfolio':'Benchmark','std':benchmarkStd,'cumulativeReturn':benchmarkCumulativeReturn,'maxDrawdown':benchmarkMaxDrawDown, 'ir':None},ignore_index=True)
portfolioMetrics['lastRunDate'] = datetime.datetime.now()
engine = sa.create_engine('mysql+mysqldb://:@:/', echo=False)
portfolioMetrics.to_sql(name='equityModelportfolioMetrics', con=engine,if_exists='replace')
attritubtionDataTable.to_sql(name='equityModelCumulativeReturns', con=engine,if_exists='replace')
for i in range(len(dailyHoldings.index)):
    if i == 0:
        dailyHoldings[i:i+1].to_sql(name='equityModelDailyHoldings', con=engine,if_exists='replace')
    else:
        dailyHoldings[i:i+1].to_sql(name='equityModelDailyHoldings', con=engine,if_exists='append')
sqlQuery = 'SELECT  cr.date, \
	( \
        SELECT securityName FROM equityModelDailyHoldings dh1 \
        WHERE dh1.date = cr.date \
        order by securityName asc \
        LIMIT 1 \
	) as securityNameOne, \
	( \
        SELECT securityName FROM equityModelDailyHoldings dh1 \
        WHERE dh1.date = cr.date \
        order by securityName desc \
        LIMIT 1 \
	) as securityNameTwo, \
	( \
        SELECT (close - tradePrice) * shares FROM equityModelDailyHoldings dh1 \
        WHERE dh1.date = cr.date \
        order by securityName asc \
        LIMIT 1 \
	) as openProfitOne, \
	( \
        SELECT (close - tradePrice) * shares FROM equityModelDailyHoldings dh1 \
        WHERE dh1.date = cr.date \
        order by securityName desc \
        LIMIT 1 \
	) as openProfitTwo \
FROM equityModelCumulativeReturns cr'
results = pd.read_sql_query(sqlQuery,con=engine)
results.to_sql(name='equityModelLineDailyHoldings', con=engine,if_exists='replace')
'''
Short Benchmark
       else:
            analysisDataFrame = pd.DataFrame({'ticker':[],'gdpPercentile':[],'gdpYoyDelta':[],'meanPriceToGdp':[],'currentStdPriceToGdp':[],'gdpGrowth':[]})
            for i in timeSeriesPanel.axes[0]:
                tickerDataFrame = pd.DataFrame(timeSeriesPanel[i][:endDate])
                tickerDataFrame = tickerDataFrame.dropna(how='any')
                tickerDataFrame['movingAverage'] = tickerDataFrame.Close.rolling(window=100).mean()
                tickerDataFrame['movingAverage20'] = tickerDataFrame.Close.rolling(window=40).mean()
                if len(tickerDataFrame.index) > 756 and tickerDataFrame.Close.iloc[-1] < tickerDataFrame.movingAverage.iloc[-1] and i == '^GSPC':
                    gdpPercentile = pd.DataFrame(weightedGDP[i])
                    gdpPercentile['yoyDelta'] = (gdpPercentile.dollar / gdpPercentile.dollar.shift(1))-1
                    gdpPercentile['year'] = gdpPercentile.index.year + 1
                    tickerDataFrame['year'] = tickerDataFrame.index.year
                    tickerDataFrame = pd.merge(gdpPercentile, tickerDataFrame, how='inner', on='year')
                    tickerDataFrame['closeToDollar'] = tickerDataFrame.Close / tickerDataFrame.dollar
                    tickerDataFrame['rollMean'] = tickerDataFrame.closeToDollar.expanding(min_periods=1).mean()
                    tickerDataFrame['rollStd'] = tickerDataFrame.closeToDollar.expanding(min_periods=1).std()
                    gdpPercentile = (tickerDataFrame['rollMean'].iloc[-1] - tickerDataFrame['closeToDollar'].iloc[-1]) / tickerDataFrame['rollStd'].iloc[-1]
                    analysisDataFrame = analysisDataFrame.append(pd.DataFrame({'ticker':i,'gdpPercentile':gdpPercentile,'gdpYoyDelta':tickerDataFrame['yoyDelta'].iloc[-1],'meanPriceToGdp':tickerDataFrame['rollMean'].iloc[-1],'currentStdPriceToGdp':gdpPercentile,'gdpGrowth':1 if tickerDataFrame['yoyDelta'].iloc[-1] > 0 else 0},index = [0]))
            analysisDataFrame = analysisDataFrame.sort_values('gdpPercentile',ascending=False)
            analysisDataFrame = analysisDataFrame[0:1]
            for j in range(len(analysisDataFrame.index)):
                analysis.append([analysisDataFrame['ticker'].iloc[j],-1,analysisDataFrame['gdpYoyDelta'].iloc[j],analysisDataFrame['meanPriceToGdp'].iloc[j],analysisDataFrame['currentStdPriceToGdp'].iloc[j]])
'''
