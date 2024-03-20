import time
import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    wait_for_clash_main_menu,
)
from pyclashbot.emulator.base import BaseEmulatorController
from pyclashbot.utils.logger import Logger


def card_mastery_state(controller: BaseEmulatorController, logger, next_state):
    logger.change_status("Going to collect card mastery rewards")

    if check_if_on_clash_main_menu(controller) is not True:
        logger.change_status(
            'Not on clash main menu for card_mastery_state() returning "restart"'
        )
        return "restart"

    if collect_card_mastery_rewards(controller, logger) is False:
        logger.change_status(
            'Failed somewhere in collect_card_mastery_rewards(), returning "restart"'
        )
        return "restart"

    return next_state


def collect_card_mastery_rewards(
    controller: BaseEmulatorController, logger: Logger
) -> bool:
    # get to card page
    logger.change_status("Collecting card mastery rewards...")
    if get_to_card_page_from_clash_main(controller, logger) == "restart":
        logger.change_status(
            "Failed to get to card page to collect mastery rewards! Returning false"
        )
        return False
    time.sleep(3)

    if not card_mastery_rewards_exist(controller):
        logger.change_status("No card mastery rewards to collect.")
        time.sleep(1)

    else:
        # while card mastery icon exists:
        while card_mastery_rewards_exist(controller):
            logger.change_status("Detected card mastery rewards")
            #   click card mastery icon
            collect_first_mastery_reward(controller)
            logger.change_status("Collected a card mastery reward!")
            logger.add_card_mastery_reward_collection()
            time.sleep(3)

    # get to clash main
    logger.change_status("Returning to clash main menu")
    controller.click((243, 600))

    # wait for main to appear
    if wait_for_clash_main_menu(controller, logger) is False:
        logger.change_status(
            "Failed to get back to clash main menu from card page! Returning false"
        )
        return False

    return True


def collect_first_mastery_reward(controller: BaseEmulatorController):
    # click the card mastery reward icon
    controller.click((270, 480))
    time.sleep(3)

    # click first card
    controller.click((105, 170))
    time.sleep(3)

    # click rewards
    for y in range(280, 520, 35):
        controller.click((200, y))

    # click deadspace a bunch
    controller.click((5, 355), clicks=15, interval=0.5)
    time.sleep(3)


def card_mastery_rewards_exist(controller: BaseEmulatorController):
    iar = controller.screenshot()
    pixels = [
        iar[460][280],
        iar[467][282],
        iar[464][279],
    ]

    for p in pixels:
        if p[2] < p[0] + p[1]:
            return False
    return True
