"""
   Copyright 2021 InfAI (CC SES)

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


from .config import *
from .logger import *
import iot.util.mqtt
import sys
import random
import time


__all__ = (
    config.__all__,
    logger.__all__
)


def handle_sigterm(signo, stack_frame):
    print("\ngot signal '{}' - exiting ...\n".format(signo))
    sys.exit(0)


def delay_start(min: int, max: int):
    delay = random.randint(min, max)
    print("delaying start for {}s".format(delay))
    time.sleep(delay)


def load_hub_id():
    try:
        with open(hub_id_path, "r") as file:
            return file.read()
    except FileNotFoundError:
        pass


def save_hub_id(id: str):
    with open(hub_id_path, "w") as file:
        file.write(id)
