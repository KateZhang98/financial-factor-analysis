# 过去20个交易日日收盘价离散系数（=标准差/均值）
        elif factor == 'price_20D_CV':
            temp_start_date =get_trading_days(end_date = start_date, count=30)[0]
            df = get_stock_factor('close_price_post',temp_start_date,end_date)
            df_std =df.rolling(window=20,min_periods = 10).std()
            df_avg = df.rolling(window=20, min_periods=10).mean()
            df = df_std / df_avg
            df = stock_df_reformat(df)
            return df[(df.index>=start_date) & (df.index<=end_date)]
        
        # 过去40个交易日日收盘价离散系数（=标准差/均值）
        elif factor == 'price_40D_CV':
            temp_start_date =get_trading_days(end_date = start_date, count=50)[0]
            df = get_stock_factor('close_price_post',temp_start_date,end_date)
            df_std =df.rolling(window=40,min_periods = 20).std()
            df_avg = df.rolling(window=40, min_periods=20).mean()
            df = df_std / df_avg
            df = stock_df_reformat(df)
            return df[(df.index>=start_date) & (df.index<=end_date)]
        
        #当前均线离散系数（5/10/20/40/60日均线的标准差/均值）
        elif factor=='avg_line_cv':
            temp_start_date = get_trading_days(end_date = start_date,count = 70)[0]
            df =get_stock_factor('close_price_post',temp_start_date,end_date)
            df_avg5 =df.rolling(window=5,min_periods =3).mean()
            df_avg10 =df.rolling(window=10,min_periods =5).mean()
            df_avg20 =df.rolling(window=20,min_periods =10).mean()
            df_avg40 =df.rolling(window=40,min_periods =20).mean()
            df_avg60 =df.rolling(window=60,min_periods =30).mean()
            avg =(df_avg5+df_avg10+df_avg20+df_avg40+df_avg60)/5
            std = (((df_avg5-avg).pow(2) +(df_avg10-avg).pow(2) +(df_avg20-avg).pow(2) +(df_avg40-avg).pow(2) +(df_avg60-avg).pow(2))/5).pow(1/2)
            df = std/avg
            df = stock_df_reformat(df)
            return df[(df.index>=start_date) & (df.index<=end_date)]
        
        #标志K线日
        elif factor =='is_k':
            temp_start_date = get_trading_days(end_date = start_date,count = 50)[0]
            
            close_price =get_stock_factor('close_price_post',temp_start_date,end_date)
            close_price = close_price.replace([0.0, np.inf, -np.inf], None)
            open_price =get_stock_factor('open_price_post',temp_start_date,end_date)
            open_price = open_price.replace([0.0, np.inf, -np.inf], None)
            h_post = get_stock_factor('highest_price_post',temp_start_date,end_date)
            h_post = h_post.replace([0.0, np.inf, -np.inf], None)
            l_post = get_stock_factor('lowest_price_post',temp_start_date,end_date)
            l_post = l_post.replace([0.0, np.inf, -np.inf], None)
            amt = get_stock_factor('turnover_value', temp_start_date, end_date)
            amt = amt.replace([0.0, np.inf, -np.inf], None)
            #涨跌幅
            n_pct = close_price/close_price.shift(1)-1
            #最高涨幅
            max_pct =h_post/close_price.shift(1)-1
            #当天最高价/20日内最低价
            min_20 = l_post.rolling(20,min_periods = 10).min()
            high_vs_20 = h_post/min_20.shift(1)
            #当日和前5日均量
            amt_5_avg = amt.rolling(window=5, min_periods=3).mean()
            amt_past5 = amt/amt_5_avg.shift(1)
            #收盘价大于40日均线
            forty_avg = close_price.rolling(40,min_periods =20).mean()
            close_vs_forty= close_price/forty_avg.shift(1)
            # 当天收盘vs当天开盘
            in_day = close_price/open_price
            
            df = n_pct.unstack().reset_index()
            df.columns = ['stock_code','date','n_pct']
            comp_dict ={
                'max_pct':max_pct,
                'close_vs_forty':close_vs_forty,
                'high_vs_20':high_vs_20,
                'amt_past5':amt_past5,
                'in_day':in_day
            }
            for comp_name,comp_df in comp_dict.items():
                temp =comp_df.unstack().reset_index()
                temp.columns= ['stock_code','date',comp_name]
            #     print(temp)
                df = pd.merge(df,temp,how = 'left',on = ['stock_code','date'])
            df.loc[(df['n_pct']>0.02)&(df['max_pct']>0.03)&(df['in_day']>1)&(df['close_vs_forty']>1)&(df['amt_past5']>0.6)&(df['high_vs_20']>1.2), 'is_k'] = 1
            df['is_k'].fillna(0,inplace = True)
            is_k = pd.pivot_table(df,values ='is_k',index='date',columns = 'stock_code',dropna= True).sort_index()
            is_k = stock_df_reformat(is_k)
            return is_k[(is_k.index>=start_date) & (is_k.index<=end_date)]
        #当天距离最近标志K线的交易天数
        elif factor =='k_interval_days':
        
        
        #当天收盘价距离标志K线收盘价的涨跌幅
        elif factor =='k_chg':
            temp_start_date = get_trading_days(end_date = start_date,count = 100)[0]
            
            is_k = get_stock_factor('is_k',temp_start_date,end_date).replace(0.0, np.nan)
            close_price_post = get_stock_factor('close_price_post',temp_start_date,end_date)
            k_close_price = close_price_post * is_k
            k_close_price.fillna(method ='ffill', inplace =True)
            k_chg =close_price_post/k_close_price
            k_chg = stock_df_reformat(k_chg)
            return k_chg[(k_chg.index>=start_date) & (k_chg.index<=end_date)]
            