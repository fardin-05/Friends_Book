def notification_data(request):
    if request.user.is_authenticated:
        notifications = request.user.notifications.filter(is_read=False)
        return {
            'unread_notifications': notifications,
            'unread_count': notifications.count()
        }
    return {}