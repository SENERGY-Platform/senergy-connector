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

logger = root_logger.getChild(__name__.split(".", 1)[-1])


class Router(threading.Thread):
    def __init__(self, client: cc_lib.client.Client, upstream_queue, cmd_prefix: str):
        super().__init__(name="upstream-router", daemon=True)
        self.__client = client
        self.__upstream_queue = upstream_queue
        self.__cmd_prefix = cmd_prefix

    def run(self) -> None:
        try:
            msg = cc_lib.client.message.Message(str())
            while True:
                topic, data = self.__upstream_queue.get()
                try:
                    if topic[0] == "event":
                        msg.data = data.decode()
                        self.__client.emmitEvent(cc_lib.client.message.EventEnvelope(topic[1], topic[2], msg))
                    elif topic[0] == "response":
                        data = json.loads(data)
                        if self.__cmd_prefix in data["command_id"]:
                            msg.data = data["data"]
                            self.__client.sendResponse(
                                cc_lib.client.message.CommandEnvelope(
                                    topic[1],
                                    topic[2],
                                    msg, data["command_id"].replace(self.__cmd_prefix, "")
                                )
                            )
                            logger.debug("response to '{}' - '{}'".format(data["command_id"], msg))
                    elif topic[0] == "fog":
                        self.__client.emmitFogMessage(topic[2], data.decode(), asynchronous=True)
                except Exception as ex:
                    logger.error(ex)
        except Exception as ex:
            logger.error(ex)
