"""
决策层后台进程
Decision Agent Background Process
"""
from django.core.management.base import BaseCommand
from services.agents.decision import DecisionAgent
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '运行决策层智能体（多智能体辩论与决策）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=300,
            help='更新间隔（秒），默认300秒（5分钟）'
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='仅执行一次，不持续运行'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        run_once = options['once']
        
        self.stdout.write(self.style.SUCCESS('Starting Decision Agent...'))
        
        agent = DecisionAgent()
        
        try:
            if run_once:
                # 仅执行一次
                decisions = agent.run()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Decision completed: {len(decisions)} decisions made'
                    )
                )
            else:
                # 持续运行
                while True:
                    try:
                        self.stdout.write(f'Running decision cycle...')
                        decisions = agent.run()
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Decision cycle completed. Made {len(decisions)} decisions'
                            )
                        )
                        
                        # 等待下一个周期
                        self.stdout.write(f'Waiting {interval} seconds...')
                        time.sleep(interval)
                        
                    except KeyboardInterrupt:
                        self.stdout.write(self.style.WARNING('Stopping Decision Agent...'))
                        break
                    except Exception as e:
                        logger.error(f'Decision cycle error: {e}')
                        self.stdout.write(
                            self.style.ERROR(f'Error in decision cycle: {e}')
                        )
                        time.sleep(interval)  # 发生错误后等待再继续
                        
        except Exception as e:
            logger.error(f'Decision Agent failed: {e}')
            self.stdout.write(self.style.ERROR(f'Decision Agent failed: {e}'))
            raise

