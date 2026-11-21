"""Сценарии на один год. Все изменения относительно базы — допущения команды."""
import csv
from pathlib import Path

with (Path(__file__).parent / "materials/baseline.csv").open() as src:
    base = {r["metric"]: float(r["unchanged"]) for r in csv.DictReader(src)}
for name, extra, active_share, activation, retained, direct in [
    ("Основной", 600, .65, 52, .04, 120000),
    ("Слабый", 100, .625, 46, .01, 180000),
]:
    families = base["families"] + extra
    # Новые доступы к услуге в апреле, июле и октябре. До первого полного месяца эффекта лаг 1 месяц.
    months = sum(n * (12 - month) * retained for month, n in [(4, 500), (7, 2000), (10, 3000)])
    gross = base["gross_mln"] + (months * 500 - direct) / 1e6
    print(name, "• Валовая прибыль, млн руб.", round(gross, 3))
    print("Группы", int(families), "• Активны", int(families * active_share + .5),
          "• Владельцы", int(base["owners"]), "• Активация, %", activation)
    print("Доп. оплаченные номеро-месяцы", round(months), "• Прямые расходы, руб.", direct)
