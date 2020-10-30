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


from iot.configuration import config, EnvVars
from iot.device_manager import DeviceManager
from iot.monitor import Monitor
from iot.mqtt import Client
from iot import upstream
from iot import downstream
from iot import fog_downstream
import time
import cc_lib
import queue


device_manager = DeviceManager()


def on_connect(client: cc_lib.client.Client):
    devices = device_manager.devices
    for device in devices.values():
        if device.state:
            client.connectDevice(device.id)


connector_client = cc_lib.client.Client()
connector_client.setConnectClbk(on_connect)

monitor = Monitor(device_manager, connector_client)

upstream_queue = queue.Queue()

mqtt_client = Client(upstream_queue)

cmd_prefix = "{}-{}-".format(EnvVars.ModuleID.value, config.DSRouter.cmd_prefix)

upstream_router = upstream.Router(connector_client, upstream_queue, cmd_prefix)
downstream_router = downstream.Router(connector_client, mqtt_client, cmd_prefix)
fog_downstream_router = fog_downstream.Router(connector_client, mqtt_client)


if __name__ == '__main__':
    while True:
        try:
            connector_client.initHub()
            break
        except cc_lib.client.HubInitializationError:
            time.sleep(10)
    connector_client.connect(reconnect=True)
    monitor.start()
    upstream_router.start()
    downstream_router.start()
    fog_downstream_router.start()
    mqtt_client.start()
    monitor.join()

