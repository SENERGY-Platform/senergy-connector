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
import json
import threading

import cc_lib

from .logger import root_logger
from .mqtt import Client

logger = root_logger.getChild(__name__.split(".", 1)[-1])


class Router(threading.Thread):
    def __init__(self, client: cc_lib.client.Client, mqtt_client: Client):
        super().__init__(name="fog-downstream-router", daemon=True)
        self.__cc = client
        self.__mqtt = mqtt_client

    def run(self) -> None:
        try:
            while True:
                msg = self.__cc.receiveFogMessage()
                logger.debug("got fog message: " + str(msg))
                self.__mqtt.publish(
                    msg.topic,
                    json.dumps(msg.payload),
                    qos=1
                )

        except Exception as ex:
            logger.error(ex)
