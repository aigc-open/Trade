"""
Django Management Command: 运行反思智能体
"""
import time
import logging
from django.core.management.base import BaseCommand
from services.agents.reflection import ReflectionAgent

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '运行反思智能体 - 经验总结与自我进化'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=3600,
            help='检查间隔（秒），默认1小时'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        
        self.stdout.write(self.style.SUCCESS(
            'Starting Reflection Agent'
        ))
        
        agent = ReflectionAgent()
        
        try:
            while True:
                self.stdout.write(f'\n[{time.strftime("%Y-%m-%d %H:%M:%S")}] Running reflection cycle...')
                
                result = agent.run()
                
                if result:
                    self.stdout.write(self.style.SUCCESS(
                        f"Review created: {result['review_created']}, "
                        f"Evolution completed: {result['evolution_completed']}"
                    ))
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nReflection agent stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Reflection agent error: {e}'))
            raise

