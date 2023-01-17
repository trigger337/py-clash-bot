import time

import numpy

from pyclashbot.bot.navigation import (
    get_to_bannerbox_from_daily_reward_collection_popup,
)
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.client import click, screenshot
from pyclashbot.memu.launcher import check_if_on_clash_main_menu


def collect_daily_challenge_rewards(logger):
    logger.change_status("Handling daily challenge rewards...")

    # should be on clash main at this point
    if not check_if_on_clash_main_menu():
        logger.change_status(
            "Failure with collect_daily_challenge_rewards bc not on main at the start"
        )
        return "restart"

    if check_if_has_daily_challenge_rewards_to_collect():
        logger.change_status("There are daily challenge rewards to collect...")

        # open daily challenge page
        click(60, 230)
        time.sleep(2)

        # check which rewards are available
        rewards_bool_list = check_for_daily_challenge_rewards_in_daily_challenge_page()
        print("rewards_bool_list: ", rewards_bool_list)

        # collect the rewards
        index = 0
        for reward in rewards_bool_list:
            if reward:
                collect_daily_reward(logger, index)
            index += 1

        logger.change_status("Done collecting daily challenge rewards...")

        # click deadspace a few times to return to clashmain
        click(20, 550, clicks=5, interval=0.33)

    else:
        logger.change_status("No daily challenge rewards to collect...")

    # should be on clash main at this point
    if not check_if_on_clash_main_menu():
        logger.change_status(
            "Failure with collect_daily_challenge_rewards bc not on main at the end"
        )
        return "restart"

    return "battlepass_reward_collection"


def collect_daily_reward(logger, reward_index):
    logger.change_status(
        "Collecting daily challenge reward index: " + str(reward_index)
    )

    daily_challenge_reward_coord_list = [
        # task 1
        (165, 235),
        # task 2
        (185, 285),
        # task 3
        (195, 365),
        # daily chest
        (185, 445),
        # weekly chest
        (180, 545),
    ]

    # increment logger
    logger.add_daily_challenge_reward_collection()
    print("Incremented logger to", logger.daily_challenge_reward_collections)

    # click the given reward coord
    coord = daily_challenge_reward_coord_list[reward_index]
    click(coord[0], coord[1])
    time.sleep(1)

    print("checking for bannerbox inventory full page")
    if check_for_bannerbox_inventory_full_popup():
        print("Bannerbox inventory  full")
        handle_bannerbox_inventory_full_popup()
    else:
        print("Bannerbox inventory not full")

    # daily and weekly coords require skipping thru the rewards in a chest
    if reward_index == 3 or reward_index == 4 or reward_index == 1:
        # click the skip button
        click(20, 550, clicks=20, interval=0.33)
        time.sleep(1)

        # reopen the daily rewards page
        click(60, 230)
        time.sleep(1)


def handle_bannerbox_inventory_full_popup():
    # go to bannerbox
    get_to_bannerbox_from_daily_reward_collection_popup()

    # click the '100 tickets' button
    click(300, 600)
    time.sleep(1)

    # click next '100 tickets' button
    click(215, 510)
    time.sleep(1)

    # click thru chest
    click(20, 440, clicks=20, interval=0.33)
    time.sleep(1)

    # close battlebox
    click(355, 70)
    time.sleep(1)

    # click reward 2 again
    click(190, 300)
    time.sleep(1)


def check_for_bannerbox_inventory_full_popup():
    iar = numpy.asarray(screenshot())

    inventory_full_text_exists = False
    for x_coord in range(160, 260):
        this_pixel = iar[200][x_coord]
        if pixel_is_equal(this_pixel, [255, 255, 255], tol=35):
            inventory_full_text_exists = True

    go_to_banner_box_text_exists = False
    for x_coord in range(160, 260):
        this_pixel = iar[450][x_coord]
        if pixel_is_equal(this_pixel, [106, 234, 118], tol=35):
            go_to_banner_box_text_exists = True

    if go_to_banner_box_text_exists and inventory_full_text_exists:
        return True
    return False


def check_if_pixels_indicate_daily_challenge_rewards_to_collect():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[209][52],
        iar[205][72],
        iar[253][67],
    ]
    color_yellow = [233, 213, 50]
    # print_pix_list(pix_list)
    for pix in pix_list:
        if not pixel_is_equal(pix, color_yellow, tol=45):
            return False
    return True


def check_if_has_daily_challenge_rewards_to_collect():
    timer = 0
    while timer < 3:
        time.sleep(0.1)
        timer += 0.1
        if check_if_pixels_indicate_daily_challenge_rewards_to_collect():
            return True
    return False


def check_for_daily_challenge_rewards_in_daily_challenge_page():
    # list of pixels that pertain to the daily challenge reward task icons in the list of daily challenge rewards
    daily_challenge_reward_coord_list = [
        (105, 225),
        (105, 285),
        (105, 355),
        (90, 440),
        (90, 550),
    ]

    # array of bools that indicate if the daily challenge reward task icons are present
    daily_challenge_exists_bool_list = []

    # check each coord in the list of daily challenge reward task icons, if the pixel is yellow, then the task reward exists, else it does not
    iar = numpy.asarray(screenshot())
    color_yellow = [255, 221, 78]
    for n in range(5):
        this_coord = daily_challenge_reward_coord_list[n]
        this_pixel = iar[this_coord[1]][this_coord[0]]
        if pixel_is_equal(this_pixel, color_yellow, tol=45):
            daily_challenge_exists_bool_list.append(True)
        else:
            daily_challenge_exists_bool_list.append(False)

    return daily_challenge_exists_bool_list
