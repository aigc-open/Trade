"""
市场数据采集器
参考 AI-Trader 项目的数据采集逻辑
"""
import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from apps.market_data.models import MarketDataModel, StockInfoModel
import akshare as ak
import yfinance as yf

logger = logging.getLogger(__name__)


class MarketDataCollector:
    """市场数据采集器"""
    
    def __init__(self):
        self.config = settings.AI_TRADER_CONFIG
        self.data_dir = self.config.get('MARKET_DATA_DIR')
        self.alphavantage_key = self.config.get('ALPHAVANTAGE_API_KEY')
        
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
    
    def collect_a_stock_data(self, symbol: str, days: int = 30) -> Dict:
        """
        采集A股数据（使用 AKShare）
        
        Args:
            symbol: 股票代码（如 "000001"）
            days: 采集天数
            
        Returns:
            Dict: 采集结果
        """
        try:
            logger.info(f"Collecting A-stock data for {symbol}")
            
            # 使用 AKShare 获取历史数据
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=(datetime.now() - timedelta(days=days)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d"),
                adjust="qfq"  # 前复权
            )
            
            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return {'success': False, 'count': 0}
            
            # 保存到数据库
            saved_count = 0
            for _, row in df.iterrows():
                try:
                    timestamp = timezone.make_aware(
                        datetime.strptime(str(row['日期']), '%Y-%m-%d')
                    )
                    
                    MarketDataModel.objects.update_or_create(
                        symbol=symbol,
                        market='A_STOCK',
                        timestamp=timestamp,
                        defaults={
                            'open': Decimal(str(row['开盘'])),
                            'high': Decimal(str(row['最高'])),
                            'low': Decimal(str(row['最低'])),
                            'close': Decimal(str(row['收盘'])),
                            'volume': int(row['成交量']),
                            'amount': Decimal(str(row.get('成交额', 0))),
                            'change_pct': Decimal(str(row.get('涨跌幅', 0))),
                            'turnover_rate': Decimal(str(row.get('换手率', 0))),
                            'data_source': 'akshare'
                        }
                    )
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Failed to save data for {symbol} on {row['日期']}: {e}")
            
            logger.info(f"Saved {saved_count} records for {symbol}")
            return {'success': True, 'count': saved_count}
            
        except Exception as e:
            logger.error(f"Failed to collect A-stock data for {symbol}: {e}")
            return {'success': False, 'error': str(e)}
    
    def collect_us_stock_data(self, symbol: str, days: int = 30) -> Dict:
        """
        采集美股数据（使用 yfinance）
        
        Args:
            symbol: 股票代码（如 "AAPL"）
            days: 采集天数
            
        Returns:
            Dict: 采集结果
        """
        try:
            logger.info(f"Collecting US stock data for {symbol}")
            
            # 使用 yfinance 获取历史数据
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=f"{days}d")
            
            if df.empty:
                logger.warning(f"No data found for {symbol}")
                return {'success': False, 'count': 0}
            
            # 保存到数据库
            saved_count = 0
            for date, row in df.iterrows():
                try:
                    timestamp = timezone.make_aware(date.to_pydatetime())
                    
                    # 计算涨跌幅
                    change_pct = ((row['Close'] - row['Open']) / row['Open'] * 100) if row['Open'] > 0 else 0
                    
                    MarketDataModel.objects.update_or_create(
                        symbol=symbol,
                        market='US_STOCK',
                        timestamp=timestamp,
                        defaults={
                            'open': Decimal(str(row['Open'])),
                            'high': Decimal(str(row['High'])),
                            'low': Decimal(str(row['Low'])),
                            'close': Decimal(str(row['Close'])),
                            'volume': int(row['Volume']),
                            'change_pct': Decimal(str(change_pct)),
                            'data_source': 'yfinance'
                        }
                    )
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Failed to save data for {symbol} on {date}: {e}")
            
            logger.info(f"Saved {saved_count} records for {symbol}")
            return {'success': True, 'count': saved_count}
            
        except Exception as e:
            logger.error(f"Failed to collect US stock data for {symbol}: {e}")
            return {'success': False, 'error': str(e)}
    
    def collect_alphavantage_data(self, symbol: str, outputsize: str = "compact") -> Dict:
        """
        使用 Alpha Vantage API 采集数据
        参考 AI-Trader 的实现
        
        Args:
            symbol: 股票代码
            outputsize: compact 或 full
            
        Returns:
            Dict: 采集结果
        """
        try:
            if not self.alphavantage_key:
                logger.warning("Alpha Vantage API key not configured")
                return {'success': False, 'error': 'API key not configured'}
            
            url = (
                f"https://www.alphavantage.co/query?"
                f"function=TIME_SERIES_DAILY&symbol={symbol}"
                f"&outputsize={outputsize}&apikey={self.alphavantage_key}"
            )
            
            response = requests.get(url)
            data = response.json()
            
            if 'Error Message' in data:
                logger.error(f"Alpha Vantage API error: {data['Error Message']}")
                return {'success': False, 'error': data['Error Message']}
            
            if 'Note' in data or 'Information' in data:
                logger.warning(f"Alpha Vantage API rate limit or info: {data}")
                return {'success': False, 'error': 'Rate limit or API info'}
            
            time_series = data.get('Time Series (Daily)', {})
            if not time_series:
                logger.warning(f"No time series data for {symbol}")
                return {'success': False, 'count': 0}
            
            # 保存到本地JSON文件
            output_file = os.path.join(self.data_dir, f"daily_prices_{symbol}.json")
            
            # 加载已存在的数据
            existing_data = self._load_existing_data(output_file)
            merged_data = self._merge_data(existing_data, data)
            
            # 保存合并后的数据
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=4)
            
            # 保存到数据库
            saved_count = 0
            for date_str, values in time_series.items():
                try:
                    timestamp = timezone.make_aware(
                        datetime.strptime(date_str, '%Y-%m-%d')
                    )
                    
                    market = self._determine_market(symbol)
                    
                    MarketDataModel.objects.update_or_create(
                        symbol=symbol,
                        market=market,
                        timestamp=timestamp,
                        defaults={
                            'open': Decimal(values['1. open']),
                            'high': Decimal(values['2. high']),
                            'low': Decimal(values['3. low']),
                            'close': Decimal(values['4. close']),
                            'volume': int(values['5. volume']),
                            'data_source': 'alphavantage',
                            'raw_data': values
                        }
                    )
                    saved_count += 1
                except Exception as e:
                    logger.error(f"Failed to save data for {symbol} on {date_str}: {e}")
            
            logger.info(f"Saved {saved_count} records for {symbol}")
            return {'success': True, 'count': saved_count}
            
        except Exception as e:
            logger.error(f"Failed to collect data from Alpha Vantage for {symbol}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _load_existing_data(self, filepath: str) -> Optional[Dict]:
        """加载已存在的数据文件"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load existing data from {filepath}: {e}")
        return None
    
    def _merge_data(self, existing_data: Optional[Dict], new_data: Dict) -> Dict:
        """合并数据：保留已存在的日期，只添加新日期"""
        if not existing_data or 'Time Series (Daily)' not in existing_data:
            return new_data
        
        existing_dates = existing_data['Time Series (Daily)']
        new_dates = new_data.get('Time Series (Daily)', {})
        
        # 合并：保留已存在的日期，添加新日期
        merged_dates = existing_dates.copy()
        for date, values in new_dates.items():
            if date not in merged_dates:
                merged_dates[date] = values
        
        # 按日期排序（降序）
        sorted_dates = dict(sorted(merged_dates.items(), reverse=True))
        
        # 更新数据
        merged_data = existing_data.copy()
        merged_data['Time Series (Daily)'] = sorted_dates
        
        # 更新 Last Refreshed
        if sorted_dates:
            merged_data['Meta Data']['3. Last Refreshed'] = list(sorted_dates.keys())[0]
        
        return merged_data
    
    def _determine_market(self, symbol: str) -> str:
        """根据股票代码确定市场类型"""
        if '.SH' in symbol or '.SZ' in symbol:
            return 'A_STOCK'
        elif '.HK' in symbol:
            return 'HK_STOCK'
        else:
            return 'US_STOCK'
    
    def batch_collect(self, symbols: List[str], market: str = 'US_STOCK') -> Dict:
        """
        批量采集数据
        
        Args:
            symbols: 股票代码列表
            market: 市场类型
            
        Returns:
            Dict: 采集结果统计
        """
        results = {
            'success_count': 0,
            'fail_count': 0,
            'total_records': 0,
            'details': []
        }
        
        for symbol in symbols:
            try:
                if market == 'A_STOCK':
                    result = self.collect_a_stock_data(symbol)
                elif market == 'US_STOCK':
                    result = self.collect_us_stock_data(symbol)
                else:
                    result = self.collect_alphavantage_data(symbol)
                
                if result.get('success'):
                    results['success_count'] += 1
                    results['total_records'] += result.get('count', 0)
                else:
                    results['fail_count'] += 1
                
                results['details'].append({
                    'symbol': symbol,
                    'result': result
                })
                
            except Exception as e:
                logger.error(f"Failed to collect data for {symbol}: {e}")
                results['fail_count'] += 1
        
        logger.info(
            f"Batch collection completed: {results['success_count']} success, "
            f"{results['fail_count']} failed, {results['total_records']} total records"
        )
        
        return results

