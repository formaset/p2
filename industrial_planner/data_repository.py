"""Имитационный репозиторий данных для примера."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from .data_models import Order, Resource, Task


class DataRepository:
    """Построитель данных для демонстрации алгоритмов планирования."""

    def __init__(self) -> None:
        self._resources: Dict[str, Resource] = {}
        self._orders: List[Order] = []
        self._populate()

    def resources(self) -> Dict[str, Resource]:
        return self._resources

    def orders(self) -> List[Order]:
        return self._orders

    def _populate(self) -> None:
        """Создаёт набор демонстрационных данных."""
        resources = [
            Resource("R1", "Лазерный станок", "станок", capacity=1.0, hourly_cost=1500, shifts=2),
            Resource("R2", "Токарный станок", "станок", capacity=1.2, hourly_cost=1200, shifts=3),
            Resource("R3", "Оператор линии", "персонал", capacity=1.0, hourly_cost=600, shifts=2),
            Resource("R4", "Инженер по настройке", "персонал", capacity=0.8, hourly_cost=950, shifts=1),
            Resource("R5", "3D-принтер", "аддитив", capacity=0.5, hourly_cost=1800, shifts=1),
        ]
        self._resources = {resource.identifier: resource for resource in resources}

        deadline = datetime.now() + timedelta(days=5)
        order1 = Order(
            identifier="Z1001",
            customer="АО Север",
            deadline=deadline,
            tasks=[
                Task("T1", "Печать корпуса", timedelta(hours=6), {"аддитив": 1}, priority=2, risk=0.2),
                Task(
                    "T2",
                    "Фрезеровка отверстий",
                    timedelta(hours=4),
                    {"станок": 1, "персонал": 1},
                    previous="T1",
                ),
                Task("T3", "Контроль качества", timedelta(hours=2), {"персонал": 1}, previous="T2", risk=0.05),
            ],
            late_penalty=10000,
        )

        deadline2 = datetime.now() + timedelta(days=4)
        order2 = Order(
            identifier="Z1002",
            customer="ООО Юг",
            deadline=deadline2,
            tasks=[
                Task("T4", "Токарная обработка", timedelta(hours=5), {"станок": 1, "персонал": 1}, priority=3),
                Task("T5", "Сборка узла", timedelta(hours=3), {"персонал": 2}, previous="T4", risk=0.15),
            ],
            late_penalty=6000,
        )

        deadline3 = datetime.now() + timedelta(days=7)
        order3 = Order(
            identifier="Z1003",
            customer="Завод Восток",
            deadline=deadline3,
            tasks=[
                Task("T6", "Лазерная резка", timedelta(hours=2), {"станок": 1}, risk=0.08),
                Task(
                    "T7",
                    "Сварка каркаса",
                    timedelta(hours=6),
                    {"персонал": 2},
                    previous="T6",
                    priority=2,
                ),
                Task("T8", "Окончательный контроль", timedelta(hours=1.5), {"персонал": 1}, previous="T7"),
            ],
            late_penalty=8000,
        )

        self._orders = [order1, order2, order3]
