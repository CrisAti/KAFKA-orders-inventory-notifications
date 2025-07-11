from confluent_kafka import Consumer
import json, os, smtplib
from email.mime.text import MIMEText
from kafka_producer import send_notification_event

MAILTRAP_USER = os.getenv("MAILTRAP_USER")
MAILTRAP_PASS = os.getenv("MAILTRAP_PASS")
MAILTRAP_HOST = "sandbox.smtp.mailtrap.io"
MAILTRAP_PORT = 2525
TO_EMAIL = os.getenv("TO_EMAIL", "test@example.com")

consumer = Consumer({
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    'group.id': 'notification-group',
    'auto.offset.reset': 'earliest'
})
consumer.subscribe(["inventory"])

print("📨 [NOTIFICATION] Escuchando eventos de 'inventory'...")

while True:
    msg = consumer.poll(1.0)
    if msg is None: continue
    if msg.error(): print("❌ Error Kafka:", msg.error()); continue

    event = json.loads(msg.value().decode("utf-8"))
    print(f"🔍 [NOTIFICATION] Evento recibido: {event}")

    if event["type"] == "inventory_updated" and event["data"].get("status") == "success":
        data = event["data"]
        order_id = data["id"]
        item = data["item"]
        quantity = data["quantity"]
        cantidadOrden = data["order_quantity"]
        subject = f"Confirmación de tu orden #{order_id}"
        body = f"Tu orden del producto '{item}' fue procesada exitosamente.\nCantidad solicitada: {cantidadOrden}."

        msg_email = MIMEText(body)
        msg_email["Subject"] = subject
        msg_email["From"] = "no-reply@microservices.test"
        msg_email["To"] = TO_EMAIL

        try:
            with smtplib.SMTP(MAILTRAP_HOST, MAILTRAP_PORT) as server:
                server.starttls()
                server.login(MAILTRAP_USER, MAILTRAP_PASS)
                server.sendmail(msg_email["From"], [TO_EMAIL], msg_email.as_string())

            print(f"✅ [NOTIFICATION] Correo enviado para orden #{order_id}")
            send_notification_event({"id": order_id, "status": "success"})

        except Exception as e:
            print(f"❌ [NOTIFICATION] Fallo al enviar correo: {str(e)}")
            send_notification_event({"id": order_id, "status": "failed"})
