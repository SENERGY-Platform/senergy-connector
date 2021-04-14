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

from iot.util import conf, init_logger, handle_sigterm, load_hub_id, save_hub_id, mqtt
from iot.device_manager import DeviceManager
from iot.monitor import Monitor
from iot import upstream
from iot import downstream
import cc_lib
import time
import queue
import signal
import os


device_manager = DeviceManager()


def on_connect(client: cc_lib.client.Client):
    for device in device_manager.devices.values():
        if device.state == "online":
            client.connect_device(device.id)


connector_client = cc_lib.client.Client(fog_processes=True)
connector_client.set_connect_clbk(on_connect)

monitor = Monitor(device_manager, connector_client)

upstream_queue = queue.Queue()

mqtt_client = mqtt.Client(upstream_queue)

cmd_prefix = "{}-{}-".format(conf.MQTTClient.id, conf.DSRouter.cmd_prefix)

upstream_router = upstream.Router(connector_client, upstream_queue, cmd_prefix)
downstream_cmd_router = downstream.command.Router(connector_client, mqtt_client, cmd_prefix)
downstream_fog_prcs_router = downstream.fog_processes.Router(connector_client, mqtt_client)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)
    init_logger(conf.Logger.level)
    hub_id = os.getenv("OVERRIDE_HUB_ID", load_hub_id())
    while True:
        try:
            if not hub_id:
                save_hub_id(connector_client.init_hub(hub_name=conf.Hub.name))
            else:
                try:
                    connector_client.init_hub(hub_id=hub_id, hub_name=conf.Hub.name)
                except cc_lib.client.HubNotFoundError as ex:
                    if not os.getenv("OVERRIDE_HUB_ID"):
                        hub_id = None
                    raise ex
            break
        except cc_lib.client.HubError:
            time.sleep(conf.Hub.init_delay)
    connector_client.connect(reconnect=True)
    monitor.start()
    upstream_router.start()
    downstream_cmd_router.start()
    downstream_fog_prcs_router.start()
    mqtt_client.start()
    monitor.join()

