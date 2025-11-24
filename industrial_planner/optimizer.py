"""Алгоритмы планирования и оптимизации."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from .data_models import ExecutionPlan, Order, Resource, ScheduledOperation, Task


class ResourceConflict(Exception):
    """Ошибка, показывающая невозможность разместить задачу."""


class Scheduler:
    """Простой эвристический планировщик с возможностью тонкой настройки."""

    def __init__(self, resources: Dict[str, Resource], cost_weight: float = 0.4, risk_weight: float = 0.2) -> None:
        self.resources = resources
        self.cost_weight = cost_weight
        self.risk_weight = risk_weight

    def _allocate_resources(self, required: Dict[str, int]) -> Dict[str, List[Resource]]:
        allocated: Dict[str, List[Resource]] = {}
        for category, quantity in required.items():
            suitable = [res for res in self.resources.values() if res.category == category]
            suitable.sort(key=lambda res: res.hourly_cost)
            if len(suitable) < quantity:
                raise ResourceConflict(f"Недостаточно ресурсов типа {category}")
            allocated[category] = suitable[:quantity]
        return allocated

    def _find_window(self, start: datetime, duration: timedelta, allocated: Dict[str, List[Resource]]) -> Tuple[datetime, datetime]:
        current_start = start
        end = start + duration
        while True:
            if all(resource.is_available(current_start, current_start + duration) for resources in allocated.values() for resource in resources):
                end = current_start + duration
                break
            current_start += timedelta(minutes=30)
        return current_start, end

    def _book_resources(self, allocated: Dict[str, List[Resource]], start: datetime, end: datetime) -> None:
        for resources in allocated.values():
            for resource in resources:
                resource.book(start, end)

    def _score(self, order: Order, task: Task) -> float:
        importance = order.base_priority()
        cost = task.estimate_cost(self.resources)
        risk = task.risk
        return importance * task.priority - self.cost_weight * cost - self.risk_weight * risk

    def build_plan(self, orders: List[Order]) -> ExecutionPlan:
        current_time = datetime.now()
        operations: List[ScheduledOperation] = []
        task_queue: List[tuple[Order, Task]] = []

        for order in orders:
            for task in order.tasks:
                task_queue.append((order, task))

        task_queue.sort(key=lambda pair: self._score(pair[0], pair[1]), reverse=True)

        finished: Dict[str, datetime] = {}
        for order, task in task_queue:
            start_point = finished.get(task.previous, current_time)
            allocated = self._allocate_resources(task.required_resources)
            start, end = self._find_window(start_point, task.duration, allocated)
            self._book_resources(allocated, start, end)
            finished[task.identifier] = end
            operations.append(
                ScheduledOperation(
                    task=task,
                    order=order,
                    start=start,
                    end=end,
                    allocated_resources=allocated,
                )
            )

        plan = ExecutionPlan(operations)
        plan.sort()
        return plan
