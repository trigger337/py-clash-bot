"""
This module contains the base class for emulator controllers.
"""

from typing import Literal
import numpy as np


class BaseEmulatorController:
    """
    Base class for emulator controllers.
    This class is used to define the interface for all emulator controllers.
    """

    def __init__(self):
        raise NotImplementedError

    def __del__(self):
        raise NotImplementedError

    def create(self):
        """
        This method is used to create the emulator.
        """
        raise NotImplementedError

    def configure(self):
        """
        This method is used to configure the emulator.
        """
        raise NotImplementedError

    def start(self):
        """
        This method is used to start the emulator.
        """
        raise NotImplementedError

    def stop(self):
        """
        This method is used to stop the emulator.
        """
        raise NotImplementedError

    def click(self, position: tuple[int, int], clicks: int = 1, interval: float = 0):
        """
        This method is used to click on the emulator screen.
        """
        raise NotImplementedError

    def swipe(
        self,
        start_position: tuple[int, int],
        end_position: tuple[int, int],
        repeat: int = 1,
        delay: float = 0,
    ):
        """
        This method is used to swipe on the emulator screen.
        """
        raise NotImplementedError

    def screenshot(self) -> np.ndarray:
        """
        This method is used to take a screenshot of the emulator screen.
        """
        raise NotImplementedError

    def install_apk(self, apk_path: str):
        """
        This method is used to install an APK on the emulator.
        """
        raise NotImplementedError

    def start_app(self, package_name: str):
        """
        This method is used to start an app on the emulator.
        """
        raise NotImplementedError

    def stop_app(self, package_name: str):
        """
        This method is used to stop an app on the emulator.
        """
        raise NotImplementedError
