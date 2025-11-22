"""
市场数据采集命令
Collect Market Data Command
"""
from django.core.management.base import BaseCommand
from services.data_collectors.market_data_collector import MarketDataCollector
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '采集市场数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--symbols',
            type=str,
            help='股票代码列表，逗号分隔（如 AAPL,TSLA,NVDA）'
        )
        parser.add_argument(
            '--market',
            type=str,
            choices=['A_STOCK', 'US_STOCK', 'ALPHAVANTAGE'],
            default='US_STOCK',
            help='市场类型'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='采集天数，默认30天'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='从文件读取股票代码列表（每行一个代码）'
        )

    def handle(self, *args, **options):
        symbols_str = options.get('symbols')
        market = options['market']
        days = options['days']
        file_path = options.get('file')
        
        # 获取股票代码列表
        symbols = []
        if symbols_str:
            symbols = [s.strip() for s in symbols_str.split(',')]
        elif file_path:
            try:
                with open(file_path, 'r') as f:
                    symbols = [line.strip() for line in f if line.strip()]
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to read file: {e}'))
                return
        else:
            self.stdout.write(self.style.ERROR('Please provide --symbols or --file'))
            return
        
        if not symbols:
            self.stdout.write(self.style.ERROR('No symbols provided'))
            return
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting data collection for {len(symbols)} symbols in {market} market'
            )
        )
        
        # 执行采集
        collector = MarketDataCollector()
        
        try:
            results = collector.batch_collect(symbols, market)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nCollection completed!\n'
                    f'Success: {results["success_count"]}\n'
                    f'Failed: {results["fail_count"]}\n'
                    f'Total records: {results["total_records"]}'
                )
            )
            
            # 显示详细结果
            for detail in results['details']:
                symbol = detail['symbol']
                result = detail['result']
                if result.get('success'):
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ {symbol}: {result.get("count", 0)} records')
                    )
                else:
                    error = result.get('error', 'Unknown error')
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ {symbol}: {error}')
                    )
                    
        except Exception as e:
            logger.error(f'Data collection failed: {e}')
            self.stdout.write(self.style.ERROR(f'Data collection failed: {e}'))
            raise

