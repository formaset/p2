"""Командная утилита для запуска планирования и симуляции."""
from __future__ import annotations

import argparse
from pathlib import Path

from .data_repository import РепозиторийДанных
from .optimizer import Планировщик
from .reporting import ГенераторОтчётов
from .simulation import ИмитационнаяМодель


def построить_парсер() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Система интеллектуального оперативного планирования производственных процессов",
    )
    parser.add_argument(
        "--отчёт",
        type=Path,
        default=Path("отчёт.txt"),
        help="Путь к файлу для сохранения краткого отчёта",
    )
    parser.add_argument(
        "--вес-стоимости",
        type=float,
        default=0.4,
        help="Вес влияния стоимости на сортировку задач",
    )
    parser.add_argument(
        "--вес-риска",
        type=float,
        default=0.2,
        help="Вес влияния рисков на сортировку задач",
    )
    return parser


def main() -> None:
    args = построить_парсер().parse_args()

    репозиторий = РепозиторийДанных()
    планировщик = Планировщик(репозиторий.ресурсы(), вес_стоимости=args.вес_стоимости, вес_риска=args.вес_риска)
    план = планировщик.построить_план(репозиторий.заказы())

    модель = ИмитационнаяМодель(план)
    симуляция = модель.выполнить()

    генератор = ГенераторОтчётов(план, симуляция)
    отчёт = генератор.подготовить_краткий()

    args.отчёт.write_text(отчёт, encoding="utf-8")
    print("Отчёт сформирован:", args.отчёт)


if __name__ == "__main__":
    main()
