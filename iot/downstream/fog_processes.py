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

__all__ = ("Router", )


from ..util import conf, get_logger, mqtt
import threading
import cc_lib


logger = get_logger(__name__.split(".", 1)[-1])


class Router(threading.Thread):
    def __init__(self, client: cc_lib.client.Client, mqtt_client: mqtt.Client):
        super().__init__(name="downstream-fog-processes-router", daemon=True)
        self.__cc = client
        self.__mqtt = mqtt_client

    def run(self) -> None:
        try:
            while True:
                envelope = self.__cc.receive_fog_processes()
                logger.debug(envelope)
                self.__mqtt.publish(
                    "{}/{}".format(conf.MQTTClient.fog_processes_pub_topic, envelope.sub_topic),
                    envelope.message,
                    qos=conf.MQTTClient.qos
                )
        except Exception as ex:
            logger.error(ex)
