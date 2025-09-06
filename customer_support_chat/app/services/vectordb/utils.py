# customer_support_chat/app/services/vectordb/utils.py
def format_timestamp(timestamp):
    from datetime import datetime
    return datetime.utcfromtimestamp(timestamp).isoformat()
