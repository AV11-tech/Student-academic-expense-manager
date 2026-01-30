from app import app, db, User, Message

with app.app_context():
    print("=== Users ===")
    users = User.query.all()
    for u in users:
        print(f"ID: {u.id}, Username: {u.username}, Role: {u.role}")
    
    print("\n=== Messages ===")
    msgs = Message.query.all()
    for m in msgs:
        sender = User.query.get(m.sender_id)
        receiver = User.query.get(m.receiver_id)
        sender_name = sender.username if sender else "Unknown"
        receiver_name = receiver.username if receiver else "Unknown"
        print(f"ID: {m.id}, From: {sender_name} (ID:{m.sender_id}), To: {receiver_name} (ID:{m.receiver_id}), Text: '{m.text}'")
