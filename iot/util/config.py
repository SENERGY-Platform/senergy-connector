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

__all__ = ("conf", )


import sevm


class MessageBrokerConfig(sevm.Config):
    host = "message-broker"
    port = 1883


class DeviceManagerConfig(sevm.Config):
    url = "http://device-manager"
    api = "devices"


class LoggerConfig(sevm.Config):
    level = "info"
    mqtt_level = "info"


class MQTTClientConfig(sevm.Config):
    clean_session = False
    event_sub_topic = "event/#"
    command_pub_topic = "command"
    command_response_sub_topic = "response/#"
    fog_processes_sub_topic = "processes/state/#"
    fog_processes_pub_topic = "processes/cmd"
    client_error_sub_topic = "error/client"
    device_error_sub_topic = "error/device/+"
    command_error_sub_topic = "error/command/+"
    keep_alive = 5
    id = "senergy-connector"
    qos = 1


class DownStreamRouterConfig(sevm.Config):
    max_command_age = 60
    cmd_prefix = "cloud-command"


class HubConfig(sevm.Config):
    name = "my-multi-gateway"
    init_delay = 15
    id_path = ".data/hub_id"


class Conf(sevm.Config):
    MB = MessageBrokerConfig
    DM = DeviceManagerConfig
    Logger = LoggerConfig
    MQTTClient = MQTTClientConfig
    DSRouter = DownStreamRouterConfig
    Hub = HubConfig


conf = Conf(prefix="CONF_")
