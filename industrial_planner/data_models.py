"""Базовые модели данных для системы планирования."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class Resource:
    """Оборудование или персонал для выполнения операций."""

    identifier: str
    name: str
    category: str
    capacity: float
    hourly_cost: float
    shifts: int = 1
    booking_schedule: List[tuple[datetime, datetime]] = field(default_factory=list)

    def is_available(self, start: datetime, end: datetime) -> bool:
        """Проверяет доступность ресурса в указанном интервале."""
        for interval_start, interval_end in self.booking_schedule:
            if not (end <= interval_start or start >= interval_end):
                return False
        return True

    def book(self, start: datetime, end: datetime) -> None:
        """Бронирует ресурс, фиксируя интервал выполнения задачи."""
        self.booking_schedule.append((start, end))

    def current_load(self) -> float:
        """Возвращает текущую суммарную длительность бронирований в часах."""
        if not self.booking_schedule:
            return 0.0
        duration = sum((finish - begin).total_seconds() / 3600 for begin, finish in self.booking_schedule)
        return duration


@dataclass
class Task:
    """Задача технологического маршрута."""

    identifier: str
    name: str
    duration: timedelta
    required_resources: Dict[str, int]
    priority: int = 1
    risk: float = 0.1
    previous: Optional[str] = None

    def estimate_cost(self, resources: Dict[str, Resource]) -> float:
        """Приблизительный расчёт стоимости операции."""
        total = 0.0
        for resource_type, quantity in self.required_resources.items():
            matching = [res for res in resources.values() if res.category == resource_type]
            if not matching:
                continue
            avg_cost = sum(res.hourly_cost for res in matching) / len(matching)
            total += avg_cost * quantity * (self.duration.total_seconds() / 3600)
        return total


@dataclass
class Order:
    """Заказ клиента, включающий последовательность задач."""

    identifier: str
    customer: str
    deadline: datetime
    tasks: List[Task]
    late_penalty: float = 0.0

    def base_priority(self) -> int:
        """Расчёт статического приоритета заказа."""
        urgency = max(1, int((self.deadline - datetime.now()).total_seconds() // 3600))
        return max(1, int(self.late_penalty) + len(self.tasks) + urgency)


@dataclass
class ScheduledOperation:
    """Плановая операция с привязкой ко времени и ресурсам."""

    task: Task
    order: Order
    start: datetime
    end: datetime
    allocated_resources: Dict[str, List[Resource]]

    def compute_metrics(self) -> Dict[str, float]:
        """Вычисляет KPI операции."""
        work_time = (self.end - self.start).total_seconds() / 3600
        total_cost = self.task.estimate_cost({res.identifier: res for resources in self.allocated_resources.values() for res in resources})
        risk = self.task.risk * 100
        return {
            "work_hours": work_time,
            "cost": total_cost,
            "risk_percent": risk,
        }


@dataclass
class ExecutionPlan:
    """Итоговый план с набором операций."""

    operations: List[ScheduledOperation]

    def sort(self) -> None:
        """Стабилизирует порядок операций по возрастанию времени начала."""
        self.operations.sort(key=lambda op: op.start)

    def find_by_order(self, identifier: str) -> List[ScheduledOperation]:
        return [op for op in self.operations if op.order.identifier == identifier]

    def total_cost(self) -> float:
        return sum(op.compute_metrics()["cost"] for op in self.operations)

    def total_load(self) -> Dict[str, float]:
        load: Dict[str, float] = {}
        for operation in self.operations:
            for resources in operation.allocated_resources.values():
                for resource in resources:
                    load.setdefault(resource.name, 0.0)
                    load[resource.name] += (operation.end - operation.start).total_seconds() / 3600
        return load
