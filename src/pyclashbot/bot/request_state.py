import random
import time
from typing import Literal

import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_clan_tab_from_clash_main,
    get_to_profile_page,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
    pixel_is_equal,
    region_is_color,
)
from pyclashbot.emulator.base import BaseEmulatorController
from pyclashbot.utils.logger import Logger
from pyclashbot.emulator.base import BaseEmulatorController


def find_request_button(controller: BaseEmulatorController):
    folder_name = "request_button"

    size: int = get_file_count(folder_name)

    names = make_reference_image_list(size)

    locations = find_references(
        controller.screenshot(),
        folder_name,
        names,
        0.88,
    )

    coord = get_first_location(locations)
    if coord is None:
        return None
    return [coord[1], coord[0]]


def request_state(
    controller: BaseEmulatorController, logger: Logger, next_state: str
) -> str:
    """
    The request state of the bot. This state is responsible for checking if the bot is in a clan,
    checking if a request can be made, and making a request if possible.

    Args:
        vm_index (int): The index of the virtual machine to run the bot on.
        logger (Logger): The logger object to log messages to.
        next_state (str): The next state to transition to after this state is complete.

    Returns:
        str: The next state to transition to after this state is complete.
    """
    logger.change_status(status="Doing request state!")
    logger.add_request_attempt()

    # if not on main: return
    clash_main_check = check_if_on_clash_main_menu(controller)
    if clash_main_check is not True:
        logger.change_status("Not on clash main for the start of request_state()")
        logger.log("These are the pixels the bot saw after failing to find clash main:")
        for pixel in clash_main_check:
            logger.log(f"   {pixel}")

        return "restart"

    # if not in a clan, return
    logger.change_status("Checking if in a clan before requesting")
    in_a_clan_return = request_state_check_if_in_a_clan(controller, logger)
    if in_a_clan_return == "restart":
        logger.change_status(status="Error 05708425 Failure with check_if_in_a_clan")
        return "restart"

    if not in_a_clan_return:
        return next_state

    # get to clan page
    logger.change_status("Getting to clan tab to request a card")
    if get_to_clan_tab_from_clash_main(controller, logger) == "restart":
        logger.change_status(status="ERROR 74842744443 Not on clan tab")
        return "restart"

    logger.update_time_of_last_request(time.time())

    # check if request exists
    if check_if_can_request_wrapper(controller):
        # do request
        if not do_request(controller, logger):
            return "restart"
    else:
        logger.change_status(status="Can't request right now.")

    # click clash main icon
    controller.click((178, 593))

    # return to clash main
    wait_for_clash_main_menu(controller, logger, deadspace_click=False)

    return next_state


def do_random_scrolling_in_request_page(
    controller: BaseEmulatorController, logger, scrolls
) -> None:
    logger.change_status(status="Doing random scrolling in request page")
    for _ in range(scrolls):
        controller.swipe((43, 350), (43, 280))
        controller.swipe((100, 385), (330, 385))
        time.sleep(1)
    logger.change_status(status="Done with random scrolling in request page")


def count_scrolls_in_request_page(controller: BaseEmulatorController) -> int:
    # scroll down, counting each scroll, until can't scroll anymore
    scrolls = 0
    while check_if_can_scroll_in_request_page(controller):
        print(f"One scroll down. Count is {scrolls}")
        controller.swipe((43, 350), (43, 280))
        controller.swipe((100, 385), (330, 385))
        scrolls += 1
        time.sleep(1)

    # close request screen with deadspace click
    controller.click((15, 300), clicks=3, interval=1)

    # reopen request page
    controller.click((77, 536))
    time.sleep(0.1)

    return scrolls


def check_if_can_scroll_in_request_page(controller: BaseEmulatorController) -> bool:
    if not region_is_color(
        controller, region=[64, 500, 293, 55], color=(222, 235, 241)
    ):
        return True
    return False


def request_state_check_if_in_a_clan(
    controller: BaseEmulatorController, logger: Logger
) -> bool | Literal["restart"]:
    # if not on clash main, reutnr
    if check_if_on_clash_main_menu(controller) is not True:
        logger.change_status(status="ERROR 385462623 Not on clash main menu")
        return "restart"

    # get to profile page
    if get_to_profile_page(controller, logger) == "restart":
        logger.change_status(
            status="Error 9076092860923485 Failure with get_to_profile_page"
        )
        return "restart"

    # check pixels for in a clan
    in_a_clan = request_state_check_pixels_for_clan_flag(controller)

    # print clan status
    if not in_a_clan:
        logger.change_status("Not in a clan, so can't request!")

    # click deadspace to leave
    controller.click((15, 300))
    if wait_for_clash_main_menu(controller, logger) is False:
        logger.change_status(
            status="Error 87258301758939 Failure with wait_for_clash_main_menu"
        )
        return "restart"

    return in_a_clan


def request_state_check_pixels_for_clan_flag(
    controller: BaseEmulatorController,
) -> bool:
    iar = controller.screenshot()

    pix_list = []
    for x_coord in range(80, 96):
        pixel = iar[445][x_coord]
        pix_list.append(pixel)

    for y_coord in range(437, 453):
        pixel = iar[y_coord][88]
        pix_list.append(pixel)

    # for every pixel in the pix_list: format to be of format [r,g,b]
    for index, pix in enumerate(pix_list):
        pix_list[index] = [pix[0], pix[1], pix[2]]

    for pix in pix_list:
        total = int(pix[0]) + int(pix[1]) + int(pix[2])

        if total < 130:
            return True

        if total > 170:
            return True

    return False


def do_request(controller: BaseEmulatorController, logger: Logger) -> None:
    logger.change_status(status="Doing request")

    # click request button
    logger.change_status(status="Clicking request button")
    controller.click((77, 536))
    time.sleep(3)

    # max scrolls
    logger.change_status(status="Counting the maximum scrolls in the request page")
    max_scrolls: int = count_scrolls_in_request_page(controller)
    logger.log(f"Found {max_scrolls} scrolls maximum in request page")
    random_scroll_amount: int = random.randint(a=0, b=max_scrolls)
    logger.log(f"Gonna do {random_scroll_amount} scrolls in request page")

    do_random_scrolling_in_request_page(
        controller, logger=logger, scrolls=random_scroll_amount
    )

    random_click_timeout = 35  # s
    random_click_start_time = time.time()

    while 1:
        if time.time() - random_click_start_time > random_click_timeout:
            logger.change_status(
                "5913578 Clicked randomly for a random card to request too many times!"
            )
            return False

        # click card
        logger.change_status(status="Clicking random card to request")
        controller.click(
            (random.randint(a=67, b=358), random.randint(a=211, b=547)),
        )
        time.sleep(3)

        logger.change_status(status="Clicking request")

        # get request button coord
        coord = find_request_button(controller)
        if coord is None:
            continue

        # Click request button coord
        controller.click(coord)

        prev_requests = logger.get_requests()

        logger.add_request()

        requests = logger.get_requests()
        logger.log(f"Incremented requests stat from {prev_requests} to {requests}")

        time.sleep(3)
        break

    return True


def check_if_can_request_wrapper(controller: BaseEmulatorController) -> bool:
    if check_for_epic_sunday_icon_with_delay(controller, 3):
        print("Detected epic sunday icon")
        return True

    if check_for_trade_cards_icon(controller):
        print("Detected trade cards icon")
        return False

    if check_for_trade_cards_icon_2(controller):
        print("Detected trade cards icon")
        return False

    if check_if_can_request_3(controller):
        return True

    if check_if_can_request(controller):
        return True

    if check_if_can_request_2(controller):
        return True

    return False


def check_if_can_request(controller: BaseEmulatorController) -> bool:
    iar = controller.screenshot()

    region_is_white = True
    for x_index in range(48, 55):
        this_pixel = iar[530][x_index]
        if not pixel_is_equal([212, 228, 255], this_pixel, tol=25):
            region_is_white = False
            break

    for y_index in range(528, 535):
        this_pixel = iar[y_index][52]
        if not pixel_is_equal([212, 228, 255], this_pixel, tol=25):
            region_is_white = False
            break

    yellow_button_exists = False
    for x_index in range(106, 118):
        this_pixel = iar[542][x_index]
        if pixel_is_equal([255, 188, 42], this_pixel, tol=25):
            yellow_button_exists = True
            break

    if region_is_white and yellow_button_exists:
        return True
    return False


def check_for_epic_sunday_icon_with_delay(controller: BaseEmulatorController, delay):
    start_time = time.time()
    while time.time() - start_time < delay:
        if check_for_epic_sunday_icon(controller):
            return True
        time.sleep(1)
    return False


def check_for_epic_sunday_icon(controller: BaseEmulatorController):
    iar = controller.screenshot()
    pixels = [
        iar[507][43],
        iar[508][120],
    ]
    colors = [
        [250, 50, 149],
        [251, 48, 149],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(colors[i], p, tol=10):
            return False
    return True


def check_if_can_request_2(controller: BaseEmulatorController) -> bool:
    if not check_line_for_color(controller, 300, 522, 300, 544, (76, 176, 255)):
        return False
    if not check_line_for_color(controller, 362, 522, 362, 544, (76, 174, 255)):
        return False
    if not check_line_for_color(controller, 106, 537, 106, 545, (255, 188, 42)):
        return False
    if not check_line_for_color(controller, 107, 537, 119, 545, (255, 188, 42)):
        return False
    if not check_line_for_color(controller, 46, 529, 57, 539, (178, 79, 244)):
        return False
    if not check_line_for_color(controller, 50, 540, 54, 527, (176, 79, 244)):
        return False
    return True


def check_for_trade_cards_icon(controller: BaseEmulatorController) -> bool:
    lines = [
        check_line_for_color(
            controller, x_1=33, y_1=502, x_2=56, y_2=502, color=(47, 69, 105)
        ),
        check_line_for_color(
            controller, x_1=56, y_1=507, x_2=108, y_2=506, color=(253, 253, 203)
        ),
        check_line_for_color(
            controller, x_1=37, y_1=515, x_2=125, y_2=557, color=(255, 188, 42)
        ),
    ]

    return all(lines)


def check_for_trade_cards_icon_2(controller: BaseEmulatorController):
    if not check_line_for_color(controller, 67, 524, 74, 534, (255, 255, 254)):
        return False
    if not check_line_for_color(controller, 90, 523, 91, 534, (255, 255, 254)):
        return False
    if not check_line_for_color(controller, 97, 536, 102, 543, (255, 253, 250)):
        return False

    if not region_is_color(controller, [50, 530, 4, 8], (212, 228, 255)):
        return False
    if not region_is_color(controller, [106, 523, 4, 8], (255, 200, 80)):
        return False
    if not region_is_color(controller, [104, 536, 12, 8], (255, 188, 42)):
        return False
    return True


def check_if_can_request_3(controller: BaseEmulatorController):
    if not region_is_color(controller, [48, 529, 8, 7], (216, 229, 255)):
        return False
    if not region_is_color(controller, [106, 538, 12, 7], (255, 188, 42)):
        return False

    return True
