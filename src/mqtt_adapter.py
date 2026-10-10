"""Optional MQTT ingestion adapter for a separately configured local broker."""

import json

from .monitor import Sample, persist


def handle_payload(connection, payload: str | bytes):
    """Validate a JSON telemetry message and store it through the monitor."""
    record = json.loads(payload)
    sample = Sample(
        machine_id=record["machine_id"],
        timestamp=record["timestamp"],
        temperature_c=record["temperature_c"],
        vibration_mm_s=record["vibration_mm_s"],
    )
    return persist(connection, sample)


def start_listener(connection, host: str = "localhost", port: int = 1883):
    """Subscribe to telemetry. This example does not implement reconnection."""
    import paho.mqtt.client as mqtt

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            client.subscribe("factory/+/telemetry")

    def on_message(client, userdata, message):
        handle_payload(connection, message.payload)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, port, 60)
    client.loop_forever()
