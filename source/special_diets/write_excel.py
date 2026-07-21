from pathlib import Path

from openpyxl import Workbook

from special_diets.program_host_client import SpecialDiet


def write_excel(special_diets: list[SpecialDiet], path: str | Path) -> None:
    """Write special-diet details to an Excel workbook.

    Each row contains the diet type and its free-text description. Host IDs are
    intentionally excluded from the export.
    """
    workbook = Workbook()
    worksheet = workbook.active

    for special_diet in special_diets:
        worksheet.append((special_diet.diet_type, special_diet.diet_description))

    workbook.save(path)
