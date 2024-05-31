import os
from dataclasses import dataclass
from typing import Optional

from bleson import get_provider, Observer
import paho.mqtt.client as mqtt

MQTT_BROKER_ADDRESS = os.getenv('MQTT_BROKER_ADDRESS', 'localhost')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', '1883'))
MQTT_TOPIC_FORMAT = os.getenv('MQTT_TOPIC_PREFIX', 'govee/{address}/{attribute}')
MQTT_QOS = int(os.getenv('MQTT_QOS', '1'))
MQTT_RETAIN = os.getenv('MQTT_RETAIN', 'true') == 'true'

mqttc: Optional[mqtt.Client] = None


@dataclass
class GoveeData:
    address: str
    name: str
    temperature: float
    humidity: float
    battery: float


def decode_govee_data(advertisement):
    mfg_data = advertisement.mfg_data
    name = advertisement.name

    if mfg_data is None or name is None:
        return None

    address = advertisement.address.address

    if name.startswith('GVH5075'):
        values = int.from_bytes(mfg_data[3:6], 'big')

        return GoveeData(
            address=address,
            name=name,
            temperature=float(values / 10000),
            humidity=float((values % 1000) / 10),
            battery=mfg_data[6] / 100,
        )

    # Other models might use this format:
    # values = int.from_bytes(mfg_data[4:7], 'big')
    # temp = float(values / 10000)
    # hum = float((values % 1000) / 10)
    # bat = mfg_data[7]

    return None


def publish_govee_data(govee_data: GoveeData):
    mqttc.publish(generate_topic(govee_data.address, 'name'), govee_data.name, qos=MQTT_QOS, retain=MQTT_RETAIN)
    mqttc.publish(generate_topic(govee_data.address, 'temperature'), govee_data.temperature, qos=MQTT_QOS, retain=MQTT_RETAIN)
    mqttc.publish(generate_topic(govee_data.address, 'humidity'), govee_data.humidity, qos=MQTT_QOS, retain=MQTT_RETAIN)
    mqttc.publish(generate_topic(govee_data.address, 'battery'), govee_data.battery, qos=MQTT_QOS, retain=MQTT_RETAIN)


def generate_topic(address, attribute):
    return MQTT_TOPIC_FORMAT.replace('{address}', address).replace('{attribute}', attribute)


def on_bluetooth_advertisement(advertisement):
    govee_data = decode_govee_data(advertisement)
    if govee_data is not None:
        publish_govee_data(govee_data)


def main():
    global mqttc

    print(f'{MQTT_BROKER_ADDRESS=}')
    print(f'{MQTT_BROKER_PORT=}')
    print(f'{MQTT_TOPIC_FORMAT=}')
    print(f'{MQTT_QOS=}')
    print(f'{MQTT_RETAIN=}')

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect(MQTT_BROKER_ADDRESS, MQTT_BROKER_PORT, 60)

    adapter = get_provider().get_adapter()
    observer = Observer(adapter)
    observer.on_advertising_data = on_bluetooth_advertisement

    observer.start()
    mqttc.loop_forever()


if __name__ == '__main__':
    main()
