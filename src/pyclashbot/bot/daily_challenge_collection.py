from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.emulator.base import BaseEmulatorController
from pyclashbot.utils.logger import Logger
import time


def collect_daily_rewards_state(controller: BaseEmulatorController, logger, next_state):
    if collect_all_daily_rewards(controller, logger) is False:
        logger.change_status("Failed to collect daily rewards")
        return "restart"

    return next_state


def collect_challenge_rewards(
    controller: BaseEmulatorController, logger, rewards
) -> bool:
    # if not on clash main, reutrn False
    if check_if_on_clash_main_menu(controller) is not True:
        logger.change_status(
            "Not on clash main at start of collect_challenge_rewards(). Returning False"
        )
        return False

    # open daily rewards menu
    controller.click((41, 206))
    time.sleep(2)

    # click first task's reward
    if rewards[0]:
        controller.click((90, 191))
        logger.change_status("Collected 1st daily challenge reward")
        logger.add_daily_reward()
        time.sleep(1)

        # click deadspace a few times
        controller.click((10, 450), clicks=5, interval=1)

        # reopen daily rewards menu
        controller.click((41, 206))
        time.sleep(2)

    # click second task's reward
    if rewards[1]:
        controller.click((90, 260))
        logger.change_status("Collected 2nd daily challenge reward")
        logger.add_daily_reward()
        time.sleep(1)

        # click deadspace a few times
        controller.click((10, 450), clicks=5, interval=1)

        # reopen daily rewards menu
        controller.click((41, 206))
        time.sleep(2)

    # click third task's reward
    if rewards[2]:
        controller.click((90, 330))
        logger.change_status("Collected 3rd daily challenge reward")
        logger.add_daily_reward()
        time.sleep(1)

    # click deadspace a bunch
    deadspace_clicks = 5
    if rewards[1]:
        deadspace_clicks = 15
    controller.click((15, 450), clicks=deadspace_clicks, interval=0.33)

    # if not on clash main, reutrn False
    if check_if_on_clash_main_menu(controller) is not True:
        logger.change_status(
            "Not on clash main at start of collect_challenge_rewards(). Returning False"
        )
        return False

    return True


def collect_daily_bonus(controller: BaseEmulatorController, logger) -> bool:
    # if not on clash main, retunr False
    if check_if_on_clash_main_menu(controller) is not True:
        logger.change_status(
            "Not on clash main at start of collect_daily_bonus(). Returning False"
        )
        return False

    # open daily rewards menu
    controller.click((41, 206))
    time.sleep(2)

    # click the daily bonus reward
    controller.click((206, 415))
    logger.add_daily_reward()
    logger.change_status("Collected daily reward chest")
    time.sleep(1)

    # click deadspace a bunch
    print("deadspace clicks")
    controller.click((10, 450), clicks=15, interval=1)

    # if not on clash main, retunr False
    if check_if_on_clash_main_menu(controller) is not True:
        logger.change_status(
            "Not on clash main at start of collect_daily_bonus(). Returning False"
        )
        return False

    return True


def collect_weekly_bonus(controller: BaseEmulatorController, logger: Logger) -> bool:
    # if not on clash main, retunr False
    if check_if_on_clash_main_menu(controller) is not True:
        logger.change_status(
            "Not on clash main at start of collect_weekly_bonus(). Returning False"
        )
        return False

    # open daily rewards menu
    controller.click((41, 206))
    time.sleep(2)

    # click the weekly bonus reward
    controller.click((197, 500))
    logger.change_status("Collected weekly reward chest")
    logger.add_daily_reward()
    time.sleep(1)

    # click deadspace a bunch
    controller.click((15, 450), clicks=15, interval=0.33)

    # if not on clash main, retunr False
    if check_if_on_clash_main_menu(controller) is not True:
        logger.change_status(
            "Not on clash main at start of collect_weekly_bonus(). Returning False"
        )
        return False

    return True


def check_if_daily_rewards_button_exists(controller: BaseEmulatorController) -> bool:
    iar = controller.screenshot()
    pixels = [
        iar[181][17],
        iar[210][48],
        iar[200][36],
        iar[195][26],
        iar[205][63],
        iar[215][45],
        iar[226][31],
        iar[216][55],
        iar[236][66],
    ]

    colors = [
        [111, 75, 13],
        [136, 90, 23],
        [129, 91, 20],
        [118, 84, 16],
        [152, 102, 33],
        [132, 88, 21],
        [136, 96, 25],
        [147, 98, 27],
        [158, 101, 33],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=35):
            return True

    return False


def collect_all_daily_rewards(controller: BaseEmulatorController, logger) -> bool:
    # if not on clash main, reutrn False
    if check_if_on_clash_main_menu(controller) is not True:
        logger.change_status(
            "Not on clash main at start of collect_daily_rewards(). Returning False"
        )
        return False

    # if daily rewards button doesnt exist, reutnr True
    if not check_if_daily_rewards_button_exists(controller):
        logger.change_status("Daily rewards button doesn't exist")
        return True

    # check which rewards are available
    rewards = check_which_rewards_are_available(controller, logger)
    if rewards is False:
        logger.change_status(
            "Error no1919 Failed with check_which_rewards_are_available()"
        )
        return False
    time.sleep(1)

    # collect the basic 3 daily rewards for completing tasks
    if rewards[0] or rewards[1] or rewards[2]:
        if collect_challenge_rewards(controller, logger, rewards) is False:
            logger.change_status("Failed to collect challenge rewards")
            return False

    # collect the daily bonus reward if it exists
    if rewards[3] and collect_daily_bonus(controller, logger) is False:
        logger.change_status("Failed to collect daily bonus reward")
        return False

    # collect the weekly bonus reward if it exists
    if rewards[4] and collect_weekly_bonus(controller, logger) is False:
        logger.change_status("Failed to collect weekly bonus reward")
        return False

    return True


def check_which_rewards_are_available(controller: BaseEmulatorController, logger):
    logger.change_status("Checking which daily rewards are available")

    # if not on clash main, return False
    if check_if_on_clash_main_menu(controller) is not True:
        time.sleep(3)
        if check_if_on_clash_main_menu(controller) is not True:
            logger.change_status(
                "Not on clash main before check_which_rewards_are_available() "
            )

    # open daily rewards menu
    controller.click((41, 206))
    time.sleep(2)

    # check which rewards are available
    rewards = check_rewards_menu_pixels(controller)

    # click deadspace a bunch
    controller.click((15, 450), clicks=3, interval=0.33)
    time.sleep(2)

    # if not on clash main, return False
    if check_if_on_clash_main_menu(controller) is not True:
        logger.change_status(
            "Not on clash main after check_which_rewards_are_available()"
        )
        return False

    positives = 0
    for _ in rewards:
        if _:
            positives += 1

    print(f"There are {positives} to collect")
    return rewards


def check_rewards_menu_pixels(controller: BaseEmulatorController):
    iar = controller.screenshot()
    pixels = [
        iar[206][117],
        iar[273][112],
        iar[341][115],
        iar[413][233],
        iar[530][216],
    ]

    colors = [
        [181, 211, 229],
        [182, 212, 230],
        [181, 211, 229],
        [224, 132, 29],
        [113, 156, 0],
    ]

    bool_list = []
    for i, p in enumerate(pixels):
        # print(p)
        this_bool = pixel_is_equal(p, colors[i], 5)
        bool_list.append(not this_bool)

    return bool_list
