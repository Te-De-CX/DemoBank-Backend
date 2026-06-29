from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

@shared_task
def send_realtime_notification(user_id, title, message, notification_type='system', data={}):
    # Create database notification
    notification = Notification.objects.create(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        data=data,
    )
    # Send via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user_{user_id}',
        {
            'type': 'notify_user',
            'data': {
                'id': notification.id,
                'title': title,
                'message': message,
                'type': notification_type,
                'data': data,
                'created_at': notification.created_at.isoformat(),
            }
        }
    )