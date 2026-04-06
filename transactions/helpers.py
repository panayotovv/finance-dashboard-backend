from django.utils.timezone import now

def time_ago(dt):
    diff = now() - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)}h ago"
    elif seconds < 172800:
        return "Yesterday"
    else:
        return f"{int(seconds // 86400)} days ago"