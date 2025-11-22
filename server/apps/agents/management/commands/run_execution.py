"""
Django Management Command: 运行执行智能体
"""
import time
import logging
from django.core.management.base import BaseCommand
from services.agents.execution import ExecutionAgent

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '运行执行智能体 - 交易执行与风险控制'

    def add_arguments(self, parser):
        parser.add_argument(
            '--portfolio',
            type=str,
            default='simulation_main',
            help='组合名称'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=30,
            help='检查间隔（秒）'
        )

    def handle(self, *args, **options):
        portfolio = options['portfolio']
        interval = options['interval']
        
        self.stdout.write(self.style.SUCCESS(
            f'Starting Execution Agent for portfolio: {portfolio}'
        ))
        
        agent = ExecutionAgent(portfolio_name=portfolio)
        
        try:
            while True:
                self.stdout.write(f'\n[{time.strftime("%Y-%m-%d %H:%M:%S")}] Running execution cycle...')
                
                result = agent.run()
                
                self.stdout.write(self.style.SUCCESS(
                    f"Executed: {result['executed']} trades, "
                    f"Monitored: {result['monitored']} positions, "
                    f"Alerts: {len(result['alerts'])}"
                ))
                
                if result['alerts']:
                    for alert in result['alerts']:
                        self.stdout.write(self.style.WARNING(
                            f"  [{alert['level']}] {alert['message']}"
                        ))
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nExecution agent stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Execution agent error: {e}'))
            raise

