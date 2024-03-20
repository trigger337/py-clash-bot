import time
from pyclashbot.emulator.base import BaseEmulatorController
from pyclashbot.emulator.memu.launcher import check_for_vm
from pyclashbot.emulator.memu.screenshot import screen_shotter
from pyclashbot.emulator.memu.client import send_click, send_swipe
from pyclashbot.emulator.memu.configure import configure_vm
from pyclashbot.emulator.memu.pmc import pmc


class MemuEmulatorController(BaseEmulatorController):
    """
    Class for controlling a MEmu emulator.
    """

    def __init__(self, vm_index: int | None = None):
        self.vm_index = vm_index if vm_index is not None else check_for_vm()
        super().__init__()

    def create(self):
        """
        This method is used to create the emulator.
        """
        raise NotImplementedError

    def configure(self):
        """
        This method is used to configure the emulator.
        """
        configure_vm(self.vm_index)

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
        for _ in range(clicks):
            send_click(self.vm_index, position[0], position[1])
            time.sleep(interval)

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
        for _ in range(repeat):
            send_swipe(
                self.vm_index,
                start_position[0],
                start_position[1],
                end_position[0],
                end_position[1],
            )
            time.sleep(delay)

    def screenshot(self):
        """
        This method is used to take a screenshot of the emulator screen.
        """
        return screen_shotter[self.vm_index]

    def install_apk(self, apk_path: str):
        """
        This method is used to install an APK on the emulator.
        """
        pmc.install_apk_vm(apk_path=apk_path, vm_index=self.vm_index)

    def start_app(self, package_name: str):
        """
        This method is used to start an app on the emulator.
        """
        pmc.start_app_vm(package_name=package_name, vm_index=self.vm_index)

    def stop_app(self, package_name: str):
        """
        This method is used to stop an app on the emulator.
        """
        pmc.stop_app_vm(package_name=package_name, vm_index=self.vm_index)
