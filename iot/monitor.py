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


from .configuration import config
from .logger import root_logger
from .device_manager import DeviceManager
from .types.device import Device
from threading import Thread
import time, requests, cc_lib


logger = root_logger.getChild(__name__.split(".", 1)[-1])


class Monitor(Thread):
    def __init__(self, device_manager: DeviceManager, client: cc_lib.client.Client):
        super().__init__(name="monitor", daemon=True)
        self.__device_manager = device_manager
        self.__client = client

    def run(self):
        logger.info("starting '{}' ...".format(self.name))
        while True:
            queried_devices = self.__queryDeviceManager()
            if queried_devices:
                self.__evaluate(queried_devices)
            time.sleep(10)

    def __queryDeviceManager(self):
        try:
            response = requests.get("{}/{}".format(config.DM.url, config.DM.api))
            if response.status_code == 200:
                return response.json()
            else:
                logger.error("could not query device-manager - '{}'".format(response.status_code))
        except requests.exceptions.RequestException as ex:
            logger.error("could not query device-manager - '{}'".format(ex))

    def __diff(self, known: dict, unknown: dict):
        known_set = set(known)
        unknown_set = set(unknown)
        missing = known_set - unknown_set
        new = unknown_set - known_set
        changed = {key for key in known_set & unknown_set if dict(known[key]) != unknown[key]}
        return missing, new, changed

    def __evaluate(self, queried_devices):
        missing_devices, new_devices, changed_devices = self.__diff(self.__device_manager.devices, queried_devices)
        updated_devices = list()
        if missing_devices:
            futures = list()
            for device_id in missing_devices:
                logger.info("can't find '{}' with id '{}'".format(
                    self.__device_manager.get(device_id).name, device_id)
                )
                futures.append((device_id, self.__client.deleteDevice(device_id, asynchronous=True)))
            for device_id, future in futures:
                future.wait()
                try:
                    future.result()
                    self.__device_manager.delete(device_id)
                except cc_lib.client.DeviceDeleteError:
                    try:
                        self.__client.disconnectDevice(device_id)
                    except (cc_lib.client.DeviceDisconnectError, cc_lib.client.NotConnectedError):
                        pass
        if new_devices:
            futures = list()
            for device_id in new_devices:
                device = Device(
                    device_id,
                    queried_devices[device_id]["name"],
                    queried_devices[device_id]["device_type"],
                    queried_devices[device_id]["state"],
                    queried_devices[device_id]["module_id"]
                )
                logger.info("found '{}' with id '{}'".format(device.name, device.id))
                futures.append((device, self.__client.addDevice(device, asynchronous=True)))
            for device, future in futures:
                future.wait()
                try:
                    future.result()
                    self.__device_manager.add(device)
                    if device.state == "online":
                        self.__client.connectDevice(device, asynchronous=True)
                except (cc_lib.client.DeviceAddError, cc_lib.client.DeviceUpdateError):
                    pass
        if changed_devices:
            futures = list()
            for device_id in changed_devices:
                device = self.__device_manager.get(device_id)
                prev_device_name = device.name
                prev_state = device.state
                device.name = queried_devices[device_id]["name"]
                device.state = queried_devices[device_id]["state"]
                # device.device_type_id = queried_devices[device_id]["device_type"]
                if device.state != prev_state:
                    if device.state == "online":
                        self.__client.connectDevice(device, asynchronous=True)
                    elif device.state == "offline":
                        self.__client.disconnectDevice(device, asynchronous=True)
                if device.name != prev_device_name:
                    futures.append((device, prev_device_name, self.__client.updateDevice(device, asynchronous=True)))
            for device, prev_device_name, future in futures:
                future.wait()
                try:
                    future.result()
                    updated_devices.append(device.id)
                except cc_lib.client.DeviceUpdateError:
                    device.name = prev_device_name
        if any((missing_devices, new_devices, updated_devices)):
            try:
                self.__client.syncHub(list(self.__device_manager.devices.values()), asynchronous=True)
            except cc_lib.client.HubError:
                pass
