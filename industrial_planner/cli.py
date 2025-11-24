"""Командная утилита для запуска планирования и симуляции."""
from __future__ import annotations

import argparse
from pathlib import Path

from .data_repository import DataRepository
from .optimizer import Scheduler
from .reporting import ReportGenerator
from .simulation import SimulationModel


def build_parser() -> argparse.ArgumentParser:
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
    args = build_parser().parse_args()

    repository = DataRepository()
    scheduler = Scheduler(repository.resources(), cost_weight=args.вес_стоимости, risk_weight=args.вес_риска)
    plan = scheduler.build_plan(repository.orders())

    model = SimulationModel(plan)
    simulation = model.run()

    generator = ReportGenerator(plan, simulation)
    report = generator.build_summary()

    args.отчёт.write_text(report, encoding="utf-8")
    print("Отчёт сформирован:", args.отчёт)


if __name__ == "__main__":
    main()
