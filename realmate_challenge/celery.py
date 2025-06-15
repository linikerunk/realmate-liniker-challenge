import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realmate_challenge.settings')

app = Celery('realmate_challenge')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configuração de tarefas periódicas
app.conf.beat_schedule = {
    'cleanup-old-conversations': {
        'task': 'chat.tasks.cleanup_old_conversations',
        'schedule': 3600.0,  # Executa a cada hora
    },
}
