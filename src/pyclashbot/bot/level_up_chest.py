import numpy
import time


from pyclashbot.emulator.base import BaseEmulatorController
from pyclashbot.utils.logger import Logger
from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal


def collect_level_up_chest(controller: BaseEmulatorController, logger: Logger) -> bool:
    logger.change_status("Checking level up chest")

    if check_if_on_clash_main_menu(controller) is not True:
        logger.change_status(
            "Not on clash main for collect_level_up_chest(). Returning False"
        )
        return False

    if not check_for_level_up_chest(controller):
        logger.change_status("No level up chest")
        return True

    # click level up chest
    print("Clicking level up chest icon")
    controller.click((17, 16))
    time.sleep(2)

    # click the level up chest
    logger.change_status("Collecting this level up chest")
    controller.click((115, 125))
    time.sleep(2)

    # increment level up chest increments
    logger.add_level_up_chest_collect()

    # click deadspace until back on clash main
    timeout = 60  # s
    start_time = time.time()
    while check_if_on_clash_main_menu(controller) is not True:
        # timeout check
        if time.time() - start_time > timeout:
            logger.change_status("Timed out waiting for level up chest to be collected")
            return False

        print("Clicking deadspace to skip thru rewards")
        controller.click((19, 450))
        time.sleep(1)

    return True


def check_for_level_up_chest(controller: BaseEmulatorController):
    iar = controller.screenshot()

    pixels = [
        iar[7][11],
        iar[8][23],
        iar[21][10],
        iar[23][23],
    ]

    colors = [
        [255, 236, 65],
        [255, 218, 70],
        [255, 203, 70],
        [255, 165, 27],
    ]

    # for p in pixels:
    # print(p)

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(p, colors[i], tol=15):
            return True

    return False


def collect_level_up_chest_state(
    controller: BaseEmulatorController, logger, next_state
):
    logger.change_status("Entered collect_level_up_chest_state()")

    # increment attempts
    logger.add_level_up_chest_attempt()

    print("Checking if on clash for this state")
    if not check_if_on_clash_main_menu(controller):
        logger.change_status("Not on clash main for this state. Returning False")
        return "restart"

    logger.change_status("Checking for level up chest")
    if not check_for_level_up_chest(controller):
        logger.change_status("No level up chest")
        return next_state

    # collect the chest
    logger.change_status("Collecting a level up chest")
    if not collect_level_up_chest(controller, logger):
        logger.change_status("Failure while collecting level up chest. Restarting...")
        return "restart"

    # if somehow not back on clash main after running this state, restart
    if not check_if_on_clash_main_menu(controller):
        logger.change_status(
            "Not on clash main after collect_level_up_chest_state(). Restarting..."
        )
        return "restart"

    logger.change_status(
        f"collect_level_up_chest_state() successful, moving to: {next_state}"
    )

    return next_state
