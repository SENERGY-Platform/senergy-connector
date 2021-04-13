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
import json
import time


logger = get_logger(__name__.split(".", 1)[-1])


class Router(threading.Thread):
    def __init__(self, client: cc_lib.client.Client, mqtt_client: mqtt.Client, cmd_prefix: str):
        super().__init__(name="downstream-command-router", daemon=True)
        self.__cc = client
        self.__mqtt = mqtt_client
        self.__cmd_prefix = cmd_prefix

    def run(self) -> None:
        try:
            while True:
                cmd = self.__cc.receive_command()
                logger.debug(cmd)
                if time.time() - cmd.timestamp <= conf.DSRouter.max_command_age:
                    self.__mqtt.publish(
                        "{}/{}/{}".format(conf.MQTTClient.command_pub_topic, cmd.device_id, cmd.service_uri),
                        json.dumps({"command_id": "{}{}".format(self.__cmd_prefix, cmd.correlation_id), "data": cmd.message.data}),
                        qos=conf.MQTTClient.qos
                    )
                else:
                    logger.warning("dropped command - max age exceeded - correlation id: {}".format(cmd.correlation_id))
        except Exception as ex:
            logger.error(ex)
