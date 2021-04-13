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

__all__ = ("conf", "hub_id_path")


import simple_env_var


@simple_env_var.configuration
class Conf:

    @simple_env_var.section
    class MB:
        host = "message-broker"
        port = 1883

    @simple_env_var.section
    class DM:
        url = "http://device-manager"
        api = "devices"

    @simple_env_var.section
    class Logger:
        level = "info"
        mqtt_level = "info"

    @simple_env_var.section
    class MQTTClient:
        clean_session = False
        event_sub_topic = "event/#"
        command_pub_topic = "command"
        command_response_sub_topic = "response/#"
        fog_processes_sub_topic = "processes/state/#"
        fog_processes_pub_topic = "processes/cmd"
        keep_alive = 5
        id = "senergy-connector"
        qos = 1

    @simple_env_var.section
    class DSRouter:
        max_command_age = 60
        cmd_prefix = "cloud-command"

    @simple_env_var.section
    class Hub:
        name = "my-multi-gateway"
        id = None


conf = Conf()

hub_id_path = ".data/hub_id"
