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


import simple_env_var
import os


@simple_env_var.configuration
class PConf:

    @simple_env_var.section
    class MB:
        host = "message-broker"
        port = 1883

    @simple_env_var.section
    class DM:
        url = "http://device-management-service"
        api = "devices"

    @simple_env_var.section
    class Logger:
        level = "info"
        mqtt_level = "info"

    @simple_env_var.section
    class MQTTClient:
        clean_session = False
        event_topic = "event/#"
        command_topic = "command"
        response_topic = "response/#"
        keep_alive = 10

    @simple_env_var.section
    class DSRouter:
        max_command_age = 60


config = PConf()


class EnvVars:

    class GatewayLocalIP:
        name = "GATEWAY_LOCAL_IP"
        value = os.getenv("GATEWAY_LOCAL_IP")

    class ModuleID:
        name = "MODULE_ID"
        value = os.getenv("MODULE_ID")
