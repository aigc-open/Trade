"""
Django Management Command: 运行规划智能体
"""
import time
import logging
from django.core.management.base import BaseCommand
from services.agents.planning import PlanningAgent

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '运行规划智能体 - 策略规划与多步推理'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=300,
            help='检查间隔（秒），默认5分钟'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        
        self.stdout.write(self.style.SUCCESS(
            'Starting Planning Agent'
        ))
        
        agent = PlanningAgent()
        
        try:
            while True:
                self.stdout.write(f'\n[{time.strftime("%Y-%m-%d %H:%M:%S")}] Running planning cycle...')
                
                result = agent.run()
                
                if result:
                    self.stdout.write(self.style.SUCCESS(
                        f"Monitored: {result['plans_monitored']} plans, "
                        f"Active: {result['active_plans']} plans"
                    ))
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nPlanning agent stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Planning agent error: {e}'))
            raise

