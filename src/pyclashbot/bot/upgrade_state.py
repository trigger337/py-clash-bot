import time
from typing import Any

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    get_to_clash_main_from_card_page,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    region_is_color,
)
from pyclashbot.memu.client import click,screenshot
from pyclashbot.utils.logger import Logger
import numpy



CARD_COORDS: list[Any] = [
    (76,227),
    (175,224),
    (257,230),
    (339,230),

    (85,370),
    (175,370),
    (257,370),
    (339,370),
]

UPGRADE_PIXEL_COORDS: list[Any] = [
    (41,304),
    (128,304),
    (218,304),
    (306,304),

    (41,447),
    (128,447),
    (218,447),
    (306,447),
]


GREEN_COLOR = [56, 228, 72]

UPGRADE_BUTTON_COORDS = [
    (75,311),
    (165,311),
    (249,311),
    (339,311),
    (75,458),
    (165,458),
    (249,458),
    (339,458),
]

SECOND_UPGRADE_BUTTON_COORDS = (236, 574)

SECOND_UPGRADE_BUTTON_COORDS_CONDITION_1 = (239, 488)

CONFIRM_UPGRADE_BUTTON_COORDS = (232, 508)

CONFIRM_UPGRADE_BUTTON_COORDS_CONDITION_1 = (242, 413)

DEADSPACE_COORD = (10, 323)

CLOSE_BUY_GOLD_POPUP_COORD = (350, 208)

CLOSE_CARD_PAGE_COORD = (355, 238)


def upgrade_cards_state(vm_index, logger: Logger, next_state):
    logger.change_status(status="Upgrade cards state")
    logger.add_card_upgrade_attempt()

    # if not on clash main, return restart
    clash_main_check = check_if_on_clash_main_menu(vm_index)
    if clash_main_check is not True:
        logger.change_status("Not on clash main at the start of upgrade_cards_state()")
        logger.log(f'There are the pixels the bot saw after failing to find clash main:')
        for pixel in clash_main_check:
            logger.log(f'   {pixel}')

        return "restart"

    # get to card page
    logger.change_status(status="Getting to card page")
    if get_to_card_page_from_clash_main(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 0751389 Failure getting to card page from clash main in Upgrade State"
        )
        return "restart"

    # get upgrade list
    logger.change_status(status="Reading which cards are upgradable")
    upgrade_list = get_upgradable_card_bool_list(vm_index, logger)

    upgradeable_cards_count = 0
    for upgrade_bool in upgrade_list:
        if upgrade_bool:
            upgradeable_cards_count += 1

    logger.change_status(f'There are {upgradeable_cards_count} upgradable cards')


    for card_index, upgrade_bool in enumerate(upgrade_list):
        if upgrade_bool:
            upgrade_card(vm_index, logger, card_index)

    logger.change_status(status="Done upgrading cards")

    # return to clash main
    if get_to_clash_main_from_card_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 1666713 Failure getting to clash main from card page after card upgrading"
        )
        return "restart"

    logger.update_time_of_last_card_upgrade(time.time())
    return next_state


def check_for_second_upgrade_button_condition_1(vm_index) -> bool:
    """
    Check if the second upgrade button condition 1 is met.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the condition is met, False otherwise.
    """
    if not check_line_for_color(vm_index, 201, 473, 203, 503, (56, 228, 72)):
        return False
    if not check_line_for_color(vm_index, 275, 477, 276, 501, (56, 228, 72)):
        return False
    if not check_line_for_color(vm_index, 348, 153, 361, 153, (229, 36, 36)):
        return False

    return True


def check_for_confirm_upgrade_button_condition_1(vm_index) -> bool:
    """
    Check if the confirm upgrade button condition 1 is met.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the condition is met, False otherwise.
    """
    if not check_line_for_color(vm_index, 201, 401, 201, 432, (56, 228, 72)):
        return False
    if not check_line_for_color(vm_index, 277, 399, 277, 431, (56, 228, 72)):
        return False
    if not check_line_for_color(vm_index, 347, 153, 361, 154, (111, 22, 29)):
        return False

    return True


def upgrade_card(vm_index, logger: Logger, card_index) -> None:
    """
    Upgrades a card if it is upgradable.

    Args:
        vm_index (int): The index of the virtual machine to perform the upgrade on.
        logger (Logger): The logger object to use for logging.
        index (int): The index of the card to upgrade.
        upgrade_list (list[bool]): A list of boolean values indicating whether each card is upgradable.

    Returns:
        None
    """
    logger.change_status(status=f"Upgrading card index: {card_index}")


    # click the card
    logger.change_status(status="Clicking the card")
    click(vm_index, CARD_COORDS[card_index][0], CARD_COORDS[card_index][1])
    time.sleep(2)

    # click the upgrade button
    logger.change_status(status="Clicking the upgrade button for this card")
    coord = UPGRADE_BUTTON_COORDS[card_index]
    click(vm_index, coord[0], coord[1])
    time.sleep(2)

    # click second upgrade button
    logger.change_status(status="Clicking the second upgrade button")
    if check_for_second_upgrade_button_condition_1(vm_index):
        click(
            vm_index,
            SECOND_UPGRADE_BUTTON_COORDS_CONDITION_1[0],
            SECOND_UPGRADE_BUTTON_COORDS_CONDITION_1[1],
        )
    else:
        click(
            vm_index,
            SECOND_UPGRADE_BUTTON_COORDS[0],
            SECOND_UPGRADE_BUTTON_COORDS[1],
        )
    time.sleep(2)

    # if gold popup doesnt exists: add to logger's upgrade stat
    if not check_for_missing_gold_popup(vm_index):
        prev_card_upgrades = logger.get_card_upgrades()
        logger.add_card_upgraded()

        card_upgrades = logger.get_card_upgrades()
        logger.log(
            f"Incremented cards upgraded from {prev_card_upgrades} to {card_upgrades}"
        )
        # click confirm upgrade button
        logger.change_status(status="Clicking the confirm upgrade button")
        if check_for_confirm_upgrade_button_condition_1(vm_index):
            click(
                vm_index,
                CONFIRM_UPGRADE_BUTTON_COORDS_CONDITION_1[0],
                CONFIRM_UPGRADE_BUTTON_COORDS_CONDITION_1[1],
            )
        else:
            click(
                vm_index,
                CONFIRM_UPGRADE_BUTTON_COORDS[0],
                CONFIRM_UPGRADE_BUTTON_COORDS[1],
            )
        time.sleep(2)

        # close card page
        click(vm_index, CLOSE_CARD_PAGE_COORD[0], CLOSE_CARD_PAGE_COORD[1])
        time.sleep(2)

        logger.change_status('Upgraded this card')
    else:
        logger.log(f'Missing gold popup exists. Skipping this upgradable card.')

    # click deadspace
    logger.change_status(status="Clicking deadspace")
    for _ in range(4):
        click(vm_index, DEADSPACE_COORD[0], DEADSPACE_COORD[1])
        time.sleep(1)




def check_if_pixel_indicates_upgradable_card( pixel) -> bool:
    r = pixel[0]
    g = pixel[1]
    b = pixel[2]

    if r > 90:
        return False
    if r < 40:
        return False

    if g > 240:
        return False
    if g < 210:
        return False

    if b > 80:
        return False
    if b < 40:
        return False

    return True



def check_for_missing_gold_popup(vm_index):
    if not check_line_for_color(
        vm_index, x_1=338, y_1=215, x_2=361, y_2=221, color=(153, 20, 17)
    ):
        return False
    if not check_line_for_color(
        vm_index, x_1=124, y_1=201, x_2=135, y_2=212, color=(255, 255, 255)
    ):
        return False

    if not check_line_for_color(vm_index, 224, 368, 236, 416, (56, 228, 72)):
        return False

    if not region_is_color(vm_index, [70, 330, 60, 70], (227, 238, 243)):
        return False

    return True


def get_upgradable_card_bool_list(vm_index, logger: Logger):
    bool_list = []

    logger.change_status(status="Checking out which cards are upgradable")

    #click a bottom card so it scrolls down the little bit (dogshit clash UI)
    click(vm_index,163,403)
    time.sleep(1)

    #deadspace click to unclick that card but keep the random scroll
    click(vm_index,14,286)
    time.sleep(0.3)

    for i, card_coord in enumerate(CARD_COORDS):
        #click the selected card
        click(vm_index, card_coord[0],card_coord[1])
        time.sleep(2)

        #see if green uprgade button exists in card context menu
        upgrade_coord = UPGRADE_PIXEL_COORDS[i]
        bool_list.append(check_if_pixel_indicates_upgradable_card(numpy.asarray(screenshot(vm_index))[upgrade_coord[1]][upgrade_coord[0]]))

    #deadspace click
    click(vm_index,14,286)

    return bool_list

if __name__ == '__main__':
    logger=Logger()
    vm_index=11

    upgrade_cards_state(vm_index, logger, 'next_state')
