from dataclasses import dataclass
from typing import Any

from perks.read_excel import PerkUpdate


@dataclass
class PerkToUpdate:
    is_weekend_ticket: bool
    food_voucher_count: int
    email: str
    current_involvement: dict[str, Any]


@dataclass
class UpdateInput:
    involvement_id: int
    form_data: dict[str, Any]


def filter_involvements(
    involvements: dict[str, Any], edit_list: list[PerkUpdate]
) -> list[PerkToUpdate]:
    """Output involvements of type COMBINED_PERKS for people in the list"""
    perks_by_email = {
        edit.email: {
            "is_weekend_ticket": edit.is_weekend_ticket,
            "food_voucher_count": edit.food_voucher_count,
        }
        for edit in edit_list
    }

    filtered_involvements = []
    for involvement in involvements:
        if involvement["email"] in perks_by_email:
            is_found = False
            for inv in involvement["involvements"]:
                if inv["type"] == "COMBINED_PERKS":
                    perks = perks_by_email[involvement["email"]]
                    filtered_involvements.append(
                        PerkToUpdate(
                            is_weekend_ticket=perks["is_weekend_ticket"],
                            food_voucher_count=perks["food_voucher_count"],
                            current_involvement=inv,
                            email=involvement["email"],
                        )
                    )
                    is_found = True
                    print(
                        f"Found combined perks involvement for {involvement['email']}"
                    )
            if not is_found:
                print(
                    f"Could not find involvement type COMBINED_PERKS for email {involvement['email']}"
                )
    return filtered_involvements


def perk_to_form_data(perks_to_update: list[PerkToUpdate]) -> list[UpdateInput]:
    """Format the data to write to API. Don't downgrade anyone's perks (or update to the current value)"""
    filtered_perks = []

    for perk in perks_to_update:
        needs_ticket_upgrade = (
            perk.current_involvement["cachedDimensions"]["ticket-type"][0]
            == "day-ticket"
            and perk.is_weekend_ticket
        )
        needs_food_voucher_upgrade = (
            perk.current_involvement["cachedAnnotations"]["tracon:mealVouchers"]
            < perk.food_voucher_count
        )

        if not needs_ticket_upgrade and not needs_food_voucher_upgrade:
            print(
                f"No need to update involvement for {perk.email}, already has weekend ticket and enough food vouchers"
            )
            continue

        form_data = {"overrides": []}

        if needs_ticket_upgrade:
            form_data["dimensions"] = {"ticket-type": ["weekend-ticket"]}
            form_data["overrides"].append("d-ticket-type")

        if needs_food_voucher_upgrade:
            form_data["annotations"] = {"tracon:mealVouchers": perk.food_voucher_count}
            form_data["overrides"].append("a-tracon-meal-vouchers")

        print(
            f"Setting {perk.email}. Needs ticket upgrade: {needs_ticket_upgrade}, food voucher upgrade: {needs_food_voucher_upgrade}, voucher count to set: {perk.food_voucher_count}"
        )
        filtered_perks.append(UpdateInput(perk.current_involvement["id"], form_data))

    return filtered_perks
