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

from .util import conf, get_logger, gen_regex, match_topic

logger = get_logger(__name__.split(".", 1)[-1])


event_topic_regex = gen_regex(conf.MQTTClient.event_sub_topic)
cmd_resp_topic_regex = gen_regex(conf.MQTTClient.command_response_sub_topic)
fog_prcs_topic_regex = gen_regex(conf.MQTTClient.fog_processes_sub_topic)
client_error_topic_regex = gen_regex(conf.MQTTClient.client_error_sub_topic)
device_error_topic_regex = gen_regex(conf.MQTTClient.device_error_sub_topic)
command_error_topic_regex = gen_regex(conf.MQTTClient.command_error_sub_topic)


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
                topic_parts = topic.split("/")
                if match_topic(topic, event_topic_regex):
                    msg.data = data.decode()
                    self.__client.send_event(cc_lib.types.message.EventEnvelope(topic_parts[1], topic_parts[2], msg))
                elif match_topic(topic, cmd_resp_topic_regex):
                    data = json.loads(data)
                    if self.__cmd_prefix in data["command_id"]:
                        msg.data = data["data"]
                        self.__client.send_command_response(
                            cc_lib.types.message.CommandResponseEnvelope(
                                device=topic_parts[1],
                                service=topic_parts[2],
                                message=msg,
                                corr_id=data["command_id"].replace(self.__cmd_prefix, "")
                            )
                        )
                        logger.debug("response to '{}' - '{}'".format(data["command_id"], msg))
                elif match_topic(topic, fog_prcs_topic_regex):
                    self.__client.send_fog_process_sync(
                        cc_lib.types.message.FogProcessesEnvelope(sub_topic="/".join(topic_parts[2:]), message=data)
                    )
                    logger.debug("fog processes snyc for '{}' - '{}'".format("/".join(topic_parts[2:]), data))
                elif match_topic(topic, client_error_topic_regex):
                    self.__client.send_client_error(
                        cc_lib.types.message.ClientErrorEnvelope(message=data)
                    )
                elif match_topic(topic, device_error_topic_regex):
                    self.__client.send_device_error(
                        cc_lib.types.message.DeviceErrorEnvelope(message=data, device=topic_parts[1])
                    )
                elif match_topic(topic, command_error_topic_regex):
                    self.__client.send_command_error(
                        cc_lib.types.message.CommandErrorEnvelope(
                            message=data,
                            corr_id=topic_parts[1].replace(self.__cmd_prefix, "") if self.__cmd_prefix in topic_parts[1] else topic_parts[1]
                        )
                    )
                else:
                    raise RuntimeError("topic '{}' unknown".format(topic))
            except Exception as ex:
                logger.error("could not route message - {}".format(ex))
