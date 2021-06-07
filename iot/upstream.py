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

from .util import conf, get_logger

logger = get_logger(__name__.split(".", 1)[-1])


event_topic_root = conf.MQTTClient.event_sub_topic.split("/", 1)[0]
cmd_resp_topic_root = conf.MQTTClient.command_response_sub_topic.split("/", 1)[0]
fog_prcs_topic_root = conf.MQTTClient.fog_processes_sub_topic.split("/", 1)[0]


class Router(threading.Thread):
    def __init__(self, client: cc_lib.client.Client, upstream_queue, cmd_prefix: str):
        super().__init__(name="upstream-router", daemon=True)
        self.__client = client
        self.__upstream_queue = upstream_queue
        self.__cmd_prefix = cmd_prefix

    def run(self) -> None:
        msg = cc_lib.types.message.DeviceMessage()
        while True:
            try:
                topic, data = self.__upstream_queue.get()
                if topic[0] == event_topic_root:
                    msg.data = data.decode()
                    self.__client.send_event(cc_lib.types.message.EventEnvelope(topic[1], topic[2], msg))
                elif topic[0] == cmd_resp_topic_root:
                    data = json.loads(data)
                    if self.__cmd_prefix in data["command_id"]:
                        msg.data = data["data"]
                        self.__client.send_command_response(
                            cc_lib.types.message.CommandResponseEnvelope(
                                device=topic[1],
                                service=topic[2],
                                message=msg,
                                corr_id=data["command_id"].replace(self.__cmd_prefix, "")
                            )
                        )
                        logger.debug("response to '{}' - '{}'".format(data["command_id"], msg))
                elif topic[0] == fog_prcs_topic_root:
                    self.__client.send_fog_process_sync(
                        cc_lib.types.message.FogProcessesEnvelope(sub_topic="/".join(topic[2:]), message=data)
                    )
                    logger.debug("fog processes snyc for '{}' - '{}'".format("/".join(topic[2:]), data))
            except Exception as ex:
                logger.error(ex)
