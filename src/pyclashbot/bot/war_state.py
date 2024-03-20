"""random import for random war plays"""

import random
import time
from typing import Literal

import numpy

from pyclashbot.bot.nav import (
    check_for_trophy_reward_menu,
    handle_trophy_reward_menu,
    check_if_on_clash_main_menu,
    get_to_clan_tab_from_clash_main,
    get_to_clash_main_from_clan_page,
    get_to_profile_page,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    find_references,
    get_file_count,
    get_first_location,
    line_is_color,
    make_reference_image_list,
    pixel_is_equal,
    region_is_color,
)
from pyclashbot.emulator.base import BaseEmulatorController
from pyclashbot.utils.logger import Logger

CARD_COORDS = [
    (143, 590),
    (211, 590),
    (269, 590),
    (343, 590),
]
CLAN_PAGE_ICON_COORD = (281, 586)
EDIT_WAR_DECK_BUTTON_COORD = (148, 413)
RANDOM_DECK_BUTTON_COORD = (265, 483)
CLOSE_WAR_DECK_EDITOR_PAGE_BUTTON = (211, 38)
START_WAR_BATTLE_BUTTON_COORD = (267, 410)
LEAVE_WAR_BATTLE_BUTTON_COORD = (204, 553)
WAR_PAGE_DEADSPACE_COORD = (15, 315)
POST_WAR_FIGHT_WAIT = 10  # seconds
WAR_BATTLE_TIMEOUT = 360  # seconds
WAR_BATTLE_START_TIMEOUT = 120  # seconds
FIND_AND_CLICK_WAR_BATTLE_ICON_TIMEOUT = 60  # seconds


def find_war_battle_icon(controller: BaseEmulatorController):
    """method to find the war battle icon image in the current image"""

    folder_name = "war_battle_icon"
    size = get_file_count(folder_name)
    names = make_reference_image_list(size)
    locations = find_references(
        controller.screenshot(),
        folder_name,
        names,
        0.9,
    )

    coord = get_first_location(locations)
    if coord is None:
        return None
    return [coord[1], coord[0]]


def war_state(controller: BaseEmulatorController, logger: Logger, next_state: str):
    """method to handle the war state of the bot"""

    logger.add_war_attempt()

    logger.change_status(status="War state")

    # if not on clash main: return
    clash_main_check = check_if_on_clash_main_menu(controller)
    if clash_main_check is not True:
        logger.change_status("Error 4848 Not on calshmain for start of war_state()")
        logger.log("These are the pixels the bot saw after failing to find clash main:")
        for pixel in clash_main_check:
            logger.log(f"   {pixel}")

        return "restart"

    # check if in a clan
    logger.change_status(status="Making sure in a clan before war battle")
    in_a_clan_check = war_state_check_if_in_a_clan(controller, logger)

    if in_a_clan_check == "restart":
        logger.change_status(
            status="Error 502835 Failure while checking if in a clan before war battle"
        )
        return "restart"

    if not in_a_clan_check:
        logger.change_status(status="Not in a clan so skipping war...")

        return next_state

    # get to clan page
    logger.change_status(status="Starting a war battle")

    logger.log("Getting to clan tab")
    if get_to_clan_tab_from_clash_main(controller, logger) == "restart":
        logger.log("Error 86868243 Took too long to get to clan tab from clash main")
        return "restart"

    # find and click battle icon
    logger.log("Finding a battle icon")
    find_battle_return = find_and_click_war_battle_icon(controller, logger)

    # handle failure to find battle icon
    if find_battle_return == "restart":
        logger.log("Error 989 Failed clicking a war battle icon. Restarting")
        return "restart"

    # handle locked war battle
    if find_battle_return == "locked":
        controller.click((175, 600))

        time.sleep(3)

        if check_for_trophy_reward_menu(controller):
            handle_trophy_reward_menu(controller, logger)
            time.sleep(3)

        if check_if_on_clash_main_menu(controller) is not True:
            logger.change_status("Failed to get to clash main after seeing locked war.")
            return "restart"

        return next_state

    time.sleep(3)

    # make deck if needed

    handle_make_deck(controller, logger)
    time.sleep(3)

    if not check_if_deck_is_ready_for_this_battle(controller):
        logger.change_status(status="No more war decks for today!")
        # click deadspace a little to close war battle windows
        controller.click(
            WAR_PAGE_DEADSPACE_COORD,
            clicks=5,
            interval=0.3,
        )
        time.sleep(0.3)

        logger.change_status(status="Getting back to clash main")
        get_to_clash_main_from_clan_page(controller, logger)

        if wait_for_clash_main_menu(controller, logger) is False:
            logger.change_status(
                status="Erorr 7784278 failed to get to clash main after exhausting war battle decks"
            )
            return "restart"

        return next_state

    # start battle
    logger.change_status(status="Starting a war battle")
    controller.click(START_WAR_BATTLE_BUTTON_COORD)
    time.sleep(3)
    logger.add_war_fight()

    # wait for battle start
    if wait_for_war_battle_start(controller, logger) == "restart":
        logger.log("Error 858258 WAited too long for war battle to begin.")
        return "restart"

    # do fight
    if do_war_battle(controller, logger) == "restart":
        logger.change_status(status="Error 58734 Failed doing war battle")
        return "restart"
    logger.change_status(status=f"Done with war battle. Waiting {POST_WAR_FIGHT_WAIT}s")
    time.sleep(POST_WAR_FIGHT_WAIT)

    # when battle end, leave battle
    controller.click(LEAVE_WAR_BATTLE_BUTTON_COORD)

    if wait_for_war_page(controller, logger) == "restart":
        logger.change_status(status="Error 5135 Waited too long for war page")
        return "restart"

    if get_to_clash_main_from_clan_page(controller, logger) == "restart":
        logger.change_status(
            status="Error 116135 Failed return to clash main after war battle"
        )
        return "restart"

    return next_state


def handle_edit_deck_page(controller: BaseEmulatorController):
    controller.click((216, 45))


def handle_pre_war_battle_page(controller: BaseEmulatorController):
    controller.click((349, 154))


def wait_for_war_page(
    controller: BaseEmulatorController, logger
) -> Literal["restart", "good"]:
    """method to wait for the war page to load after leaving a war battle"""

    logger.change_status(status="Waiting for war page")
    start_time: float = time.time()
    while not check_if_on_war_page(controller):
        time_taken: float = time.time() - start_time
        if time_taken > 45:
            logger.change_status(
                status="Error 1109572435 WAited too long for war page after leaving war battle"
            )
            return "restart"

        # random click hell
        if random.randint(0, 2) == 0:
            if random.randint(0, 1) == 1:
                handle_edit_deck_page(controller)
            else:
                handle_pre_war_battle_page(controller)

    logger.log("Done waiting for war page")
    return "good"


def do_war_battle(
    controller: BaseEmulatorController, logger
) -> Literal["restart", "good"]:
    """method to do the fighting in a war battle.
    Pretty much throws the match but it doesnt matter"""

    start_time = time.time()
    logger.change_status(status="Starting war fighting")
    while check_if_in_war_battle(controller):
        time_taken = time.time() - start_time
        if time_taken > WAR_BATTLE_TIMEOUT:
            logger.change_status(status="Error 658725 Ran war fight loop too long")
            return "restart"

        # click a random card
        logger.change_status(status="Doing a random war play")

        random_card_coord = random.choice(CARD_COORDS)
        controller.click(random_card_coord)
        time.sleep(0.33)

        # click a random play coord
        random_play_coord = (random.randint(63, 205), random.randint(55, 455))
        controller.click(random_play_coord)
        time.sleep(9)

    logger.change_status(status="Done with this war fight")
    return "good"


def wait_for_war_battle_start(
    controller: BaseEmulatorController, logger
) -> Literal["restart", "good"]:
    """method to wait until the war battle begins, with a timeout"""

    logger.change_status(status="Waiting for war battle start")

    start_time = time.time()

    while not check_if_in_war_battle(controller):
        time.sleep(3)

        time_taken = time.time() - start_time

        if time_taken > WAR_BATTLE_START_TIMEOUT:
            logger.change_status(
                status="Error 98246572 Failure waiting for war battle start"
            )
            return "restart"

    logger.log("Waiting for war battle start")
    return "good"


def check_if_in_war_battle2(controller: BaseEmulatorController):
    iar = controller.screenshot()

    pixels = [
        iar[546][177],
        iar[561][238],
        iar[553][215],
    ]

    colors = [
        [255, 187, 104],
        [255, 175, 78],
        [255, 255, 255],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=10):
            return False

    return True


def check_if_in_war_battle(controller: BaseEmulatorController) -> bool:
    """method to check if the war battle screen still exists"""
    timeout = 3  # s
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_if_in_war_battle2(controller):
            print("Using patch job for check_if_in_war_battle()")
            controller.click((200, 550))
            return False

        if not line_is_color(
            controller, x_1=51, y_1=515, x_2=68, y_2=520, color=(255, 255, 255)
        ):
            continue

        return True

    return False


def check_if_deck_is_ready_for_this_battle(controller: BaseEmulatorController) -> bool:
    """method to scan pixels in the image of
    this war battle page to see if the deck is good to go"""

    if not region_is_color(controller, [230, 398, 17, 6], (255, 200, 79)):
        return False
    if not region_is_color(controller, [240, 427, 30, 5], (255, 188, 43)):
        return False

    if not check_line_for_color(controller, 340, 161, 354, 162, (229, 36, 36)):
        return False
    return True


def handle_make_deck(
    controller: BaseEmulatorController, logger: Logger
) -> Literal["good deck", "made deck"]:
    """method to make a fresh war deck
    if this account doesn't have one made yet"""

    # if the deck is ready to go, just return
    if check_if_deck_is_ready_for_this_battle(controller):
        logger.log("Deck is good to go. No need to make a new one")

        return "good deck"

    logger.change_status(status="Setting up a deck for this war match")
    # click edit deck button
    print("clicking edit deck button")
    controller.click(EDIT_WAR_DECK_BUTTON_COORD)
    time.sleep(3)

    # click random deck button
    print("clicking random deck button")
    controller.click(RANDOM_DECK_BUTTON_COORD)
    time.sleep(3)

    # close deck editor
    print("Closing deck editor")
    controller.click(CLOSE_WAR_DECK_EDITOR_PAGE_BUTTON)
    time.sleep(3)
    return "made deck"


def check_for_locked_clan_war_screen(controller: BaseEmulatorController):
    iar = controller.screenshot()
    pixels = [
        iar[292][125],
        iar[292][281],
        iar[586][238],
        iar[589][317],
        iar[196][215],
    ]

    colors = [
        [254, 80, 141],
        [252, 78, 139],
        [138, 103, 70],
        [140, 105, 72],
        [121, 0, 255],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(p, colors[i], tol=10):
            return False
    return True


def find_and_click_war_battle_icon(
    controller: BaseEmulatorController, logger
) -> Literal["restart", "good"]:
    """method to cycle through the various clan
    pages while searching for a war battle icon to click"""

    start_time = time.time()
    # FIND_AND_CLICK_WAR_BATTLE_ICON_TIMEOUT

    while time.time() - start_time < FIND_AND_CLICK_WAR_BATTLE_ICON_TIMEOUT:
        if check_for_locked_clan_war_screen(controller):
            logger.change_status("Clan war is locked. Skipping war battle...")
            return "locked"

        coord = find_war_battle_icon(controller)

        if coord is None:
            if random.randint(0, 1) == 1:
                controller.click(CLAN_PAGE_ICON_COORD)
                time.sleep(1.5)

            if random.randint(0, 1) == 1:
                controller.swipe((215, 300), (215, 400))
                time.sleep(1.5)
            continue

        controller.click(coord)
        return "good"

    logger.change_status(
        "Failed to find_and_click_war_battle_icon(), returning restart"
    )
    return "restart"


def check_if_on_war_page(controller: BaseEmulatorController):
    """method to check pixels to see if bot is on the war page"""

    if not check_line_for_color(
        controller, x_1=19, y_1=16, x_2=59, y_2=59, color=(144, 108, 255)
    ):
        return False
    if not check_line_for_color(
        controller, x_1=61, y_1=18, x_2=51, y_2=58, color=(144, 107, 255)
    ):
        return False
    if not check_line_for_color(
        controller, x_1=31, y_1=43, x_2=51, y_2=45, color=(226, 219, 228)
    ):
        return False

    if not region_is_color(controller, [225, 610, 25, 10], (80, 118, 153)):
        return False
    if not region_is_color(controller, [300, 610, 30, 14], (80, 118, 153)):
        return False

    return True


def war_state_check_if_in_a_clan(controller: BaseEmulatorController, logger: Logger):
    """method to handle the process of cehcking if the user in in a clan"""

    # get to profile page
    if get_to_profile_page(controller, logger) == "restart":
        logger.change_status(
            status="Error 90723563485 Failure with get_to_profile_page"
        )
        return "restart"

    # check pixels for in a clan
    in_a_clan = war_state_check_pixels_for_clan_flag(controller)

    # click deadspace to leave
    controller.click((15, 300))
    if wait_for_clash_main_menu(controller, logger) is False:
        logger.change_status(
            status="Error 872356739 Failure with wait_for_clash_main_menu"
        )
        return "restart"

    return in_a_clan


def war_state_check_pixels_for_clan_flag(controller: BaseEmulatorController):
    """method to check the pixels on the clash main
    user profile page to see if the user is in a clan"""

    iar = controller.screenshot()

    for x_index in range(78, 97):
        this_pixel = iar[446][x_index]
        if not pixel_is_equal([51, 51, 51], this_pixel, tol=25):
            return True

    for y_index in range(437, 455):
        this_pixel = iar[y_index][87]
        if not pixel_is_equal([51, 51, 51], this_pixel, tol=25):
            return True

    return False
