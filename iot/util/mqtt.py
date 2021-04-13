"""
   Copyright 2020 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

__all__ = ("Client", )


from . import conf, get_logger, logging_levels
import paho.mqtt.client
import logging
import threading
import time


logger = get_logger(__name__.split(".", 1)[-1])

mqtt_logger = logging.getLogger("mqtt-client")
mqtt_logger.setLevel(logging_levels.setdefault(conf.Logger.mqtt_level, "info"))


class Client(threading.Thread):
    def __init__(self, upstream_queue):
        super().__init__(name="mqtt", daemon=True)
        self.__upstream_queue = upstream_queue
        self.__mqtt = paho.mqtt.client.Client(
            client_id=conf.MQTTClient.id,
            clean_session=conf.MQTTClient.clean_session
        )
        self.__mqtt.on_connect = self.__onConnect
        self.__mqtt.on_disconnect = self.__onDisconnect
        self.__mqtt.on_message = self.__onMessage
        self.__mqtt.enable_logger(mqtt_logger)

    def run(self) -> None:
        while True:
            try:
                self.__mqtt.connect(conf.MB.host, conf.MB.port, keepalive=conf.MQTTClient.keep_alive)
                self.__mqtt.loop_forever()
            except Exception as ex:
                logger.error(
                    "could not connect to '{}' on '{}' - {}".format(conf.MB.host, conf.MB.port, ex)
                )
            time.sleep(5)

    def __onConnect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("connected to '{}'".format(conf.MB.host))
            self.__mqtt.subscribe(conf.MQTTClient.event_sub_topic)
            self.__mqtt.subscribe(conf.MQTTClient.command_response_sub_topic)
        else:
            logger.error("could not connect to '{}' - {}".format(conf.MB.host, paho.mqtt.client.connack_string(rc)))

    def __onDisconnect(self, client, userdata, rc):
        if rc == 0:
            logger.info("disconnected from '{}'".format(conf.MB.host))
        else:
            logger.warning("disconnected from '{}' unexpectedly".format(conf.MB.host))

    def __onMessage(self, client, userdata, message: paho.mqtt.client.MQTTMessage):
        try:
            self.__upstream_queue.put_nowait((message.topic.split("/"), message.payload))
        except Exception as ex:
            logger.error(ex)

    def publish(self, topic: str, payload: str, qos: int) -> None:
        try:
            msg_info = self.__mqtt.publish(topic=topic, payload=payload, qos=qos, retain=False)
            if msg_info.rc == paho.mqtt.client.MQTT_ERR_SUCCESS:
                logger.debug("publish '{}' - (q{}, m{})".format(payload, qos, msg_info.mid))
            elif msg_info.rc == paho.mqtt.client.MQTT_ERR_NO_CONN:
                logger.error("not connected")
            else:
                logger.error(paho.mqtt.client.error_string(msg_info.rc).replace(".", "").lower())
        except (ValueError, OSError) as ex:
            logger.error(ex)

    def subscribe(self, topic: str, qos: int) -> None:
        self.__mqtt.subscribe(topic, qos)
