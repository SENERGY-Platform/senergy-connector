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


__all__ = ("DeviceManager", "DeviceState")


from .types import Device
import typing
import threading


class DeviceState:
    online = "online"
    offline = "offline"


class DeviceManager:

    def __init__(self):
        self.__device_pool = dict()
        self.__lock = threading.Lock()

    def add(self, device: Device) -> None:
        if not isinstance(device, Device):
            raise TypeError
        self.__lock.acquire()
        if device.id not in self.__device_pool:
            self.__device_pool[device.id] = device
        self.__lock.release()

    def delete(self, device_id: str) -> None:
        if not isinstance(device_id, str):
            raise TypeError
        self.__lock.acquire()
        try:
            del self.__device_pool[device_id]
        except KeyError:
            pass
        self.__lock.release()

    def get(self, device_id: str) -> Device:
        if not isinstance(device_id, str):
            raise TypeError
        self.__lock.acquire()
        try:
            device = self.__device_pool[device_id]
        except KeyError:
            self.__lock.release()
            raise
        self.__lock.release()
        return device

    def clear(self) -> None:
        self.__lock.acquire()
        self.__device_pool.clear()
        self.__lock.release()

    @property
    def devices(self) -> typing.Dict[str, Device]:
        self.__lock.acquire()
        devices = self.__device_pool.copy()
        self.__lock.release()
        return devices
