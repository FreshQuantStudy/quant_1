import numpy as np
import pandas as pd
import talib as tl 


class Portfolio(object):
    def __init__(self, df):
        self.status = 0
        self.capital = 1000000
        self.volume = 0.0
        self.df = df[::-1]
        self.df.index = pd.to_datetime(self.df.index)
        
    def calc_ma15_portfolio(self):
        df = self.df.copy()
        
        df['ma15'] = tl.SMA(df['close'].values, 15)
        df.dropna(axis=0, inplace=True)
        df['buy_ma15'] = df['close'] > df['ma15']
        df['sale_ma15'] = df['close'] < df['ma15']
    
        pofolio_change = []
        for buy, sale, close in zip(df['buy_ma15'], df['sale_ma15'], df['close']):
            if self.status == 0 and buy == 1:
                self.volume = self.capital / close
                self.capital = 0
                self.status = 1
            if self.status == 1 and sale == 1:
                self.capital = self.volume * close
                self.volume = 0
                self.status = 0
                
            if self.status == 0:
                pofolio_change.append(self.capital)
            if self.status == 1:
                pofolio_change.append(self.volume * close)
        
        df['portfolio'] = pofolio_change
        df['daily_return'] = df['portfolio'].shift(-1) / df['portfolio'] - 1
        
        return df
    
    @staticmethod
    def print_statistical_info(df):
        final_portfolio_value = df['portfolio'][-1]
        cumulative_returns = final_portfolio_value/1000000 - 1
        average_daily_return = cumulative_returns / df.shape[0]
        annual_return = average_daily_return * 252
        
        daily_return_var = df['daily_return'].var()
        volatility = np.sqrt(252*daily_return_var)
        sharpe_ratio = (annual_return - 0.05) / volatility
        
        print('最终资产价值 Final portfolio value: ${:,.2f}'.format(final_portfolio_value))
        print('累计回报率 Cumulative returns: {:.2f} %'.format(cumulative_returns))
        print('平均日收益率 Average daily return: {:.5f} %'.format(average_daily_return))
        print('年收益 Annual return: {:.2f} %'.format(annual_return))
        
        print('日收益率方差 Var. daily return: {:.4f}'.format(daily_return_var))
        print('波动率 Volatility: {:.2f}'.format(volatility))
        print('夏普指数 Sharpe ratio: {:.2f}'.format(sharpe_ratio))
                
        mdd = 0.0
        lddd = ''
        tdd = 0
        hdd = 0.0
        
        for i in range(1, df.shape[0]):
            c_hdd = df['portfolio'][:i].max()
            c_ldd = df['portfolio'][i]
            c_mdd = 1 - c_ldd/c_hdd
            c_tdd = (df['portfolio'].index[i] - df['portfolio'][:i].argmax()).days
            c_lddd = df['portfolio'][:i].argmax()
            
            if c_mdd > mdd:
                mdd = c_mdd
                lddd = c_lddd
                tdd = c_tdd
                hdd = c_hdd
                ldd = c_ldd
                    
        
        print('\n最大回撤率 Max. drawdown: {:.2f} %'.format(mdd*100))
        print('回撤时间 Longest drawdown duration: %s ' % lddd)
        print('最长回撤时间 Time. drawdown: %s days' % tdd)
        print('回撤最高点位 High. drawdown: {:,.2f}'.format(hdd))
        print('回撤最低点位 Low. drawdown: {:,.2f}'.format(ldd))
        
        