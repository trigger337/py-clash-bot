from pyclashbot.emulator.base import BaseEmulatorController
from pyclashbot.emulator.memu.screenshot import screen_shotter
from pyclashbot.emulator.memu.client import send_click, send_swipe
from pyclashbot.emulator.memu.configure import configure_vm


class MemuEmulatorController(BaseEmulatorController):
    """
    Class for controlling a MEmu emulator.
    """

    def __init__(self, vm_index: int):
        self.vm_index = vm_index
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

    def click(self, position: tuple[int, int]):
        """
        This method is used to click on the emulator screen.
        """
        send_click(self.vm_index, position[0], position[1])

    def swipe(
        self,
        start_position: tuple[int, int],
        end_position: tuple[int, int],
    ):
        """
        This method is used to swipe on the emulator screen.
        """
        send_swipe(
            self.vm_index,
            start_position[0],
            start_position[1],
            end_position[0],
            end_position[1],
        )

    def screenshot(self):
        """
        This method is used to take a screenshot of the emulator screen.
        """
        return screen_shotter[self.vm_index]
