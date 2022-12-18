import PySimpleGUI as sg

from pyclashbot.interface.theme import THEME

sg.theme(THEME)


def stat_box(stat_name: str, size=(5, 1)) -> sg.Text:
    return sg.Text(
        "0",
        key=stat_name,
        relief=sg.RELIEF_SUNKEN,
        text_color="blue",
        size=size,
    )


battle_stats_title = [
    [
        sg.Text("Wins: "),
    ],
    [
        sg.Text("Losses: "),
    ],
    [
        sg.Text("Cards Played: "),
    ],
    [
        sg.Text("2v2 Fights: "),
    ],
    [
        sg.Text("War Battles Fought: "),
    ],
]

battle_stats_values = [
    [
        stat_box("wins"),
    ],
    [
        stat_box("losses"),
    ],
    [
        stat_box("cards_played"),
    ],
    [
        stat_box("fights"),
    ],
    [
        stat_box("war_battles_fought"),
    ],
]

battle_stats = [
    [
        sg.Column(battle_stats_title, element_justification="right"),
        sg.Column(battle_stats_values, element_justification="left"),
    ]
]

progress_stats_titles = [
    [
        sg.Text("Requests: "),
    ],
    [
        sg.Text("Chests Unlocked: "),
    ],
    [
        sg.Text("Cards Upgraded: "),
    ],
    [
        sg.Text("Account Switches: "),
    ],
    [
        sg.Text("Automatic Restarts: "),
    ],
    [
        sg.Text("Restarts b/c Failure: "),
    ],
]

progress_stats_values = [
    [
        stat_box("requests"),
    ],
    [
        stat_box("chests_unlocked"),
    ],
    [
        stat_box("cards_upgraded"),
    ],
    [
        stat_box("account_switches"),
    ],
    [
        stat_box("auto_restarts"),
    ],
    [
        stat_box("restarts_after_failure"),
    ],
]

progress_stats = [
    [
        sg.Column(progress_stats_titles, element_justification="right"),
        sg.Column(progress_stats_values, element_justification="left"),
    ]
]

collections_stats_titles = [
    [
        sg.Text(
            "Card Mastery Reward Collections: ",
        ),
    ],
    [
        sg.Text("Battlepass Reward Collections: "),
    ],
    [
        sg.Text("Level Up Chest Collections: "),
    ],
    [
        sg.Text("Free Offer Collections: "),
    ],
    [
        sg.Text("War Chest collections: "),
    ],
    [
        sg.Text("Daily Challenge Reward Collections: "),
    ],
    
]

collections_stats_values = [
    [
        stat_box("card_mastery_reward_collections"),
    ],
    [
        stat_box("battlepass_rewards_collections"),
    ],
    [
        stat_box("level_up_chest_collections"),
    ],
    [
        stat_box("free_offer_collections"),
    ],
    [
        stat_box("war_chest_collections"),
    ],
    [
        stat_box("daily_challenge_reward_collections"),
    ],
    
]

collections_stats = [
    [
        sg.Column(collections_stats_titles, element_justification="right"),
        sg.Column(collections_stats_values, element_justification="left"),
    ]
]
