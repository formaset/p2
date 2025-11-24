"""Формирование детализированных отчётов."""
from __future__ import annotations

from typing import List

from .data_models import ExecutionPlan
from .simulation import SimulationResult


class ReportGenerator:
    """Подготавливает текстовые отчёты для руководства и диспетчеров."""

    def __init__(self, plan: ExecutionPlan, simulation: SimulationResult) -> None:
        self.plan = plan
        self.simulation = simulation

    def _operation_line(self, index: int, operation) -> str:
        resources = [f"{res.name} ({res.category})" for resources in operation.allocated_resources.values() for res in resources]
        return (
            f"{index}. {operation.task.name} для заказа {operation.order.identifier}"
            f" c {operation.start:%d.%m %H:%M} по {operation.end:%d.%m %H:%M} \n"
            f"   Ресурсы: {', '.join(resources)}\n"
        )

    def build_summary(self) -> str:
        lines: List[str] = ["=== Итоговый план ==="]
        for number, operation in enumerate(self.plan.operations, start=1):
            lines.append(self._operation_line(number, operation))

        lines.append("=== KPI симуляции ===")
        lines.append(f"Общая стоимость с учётом рисков: {self.simulation.total_cost:,.2f} руб.")
        lines.append(f"Средний риск: {self.simulation.mean_risk:.2f} %")
        lines.append(f"Средний коэффициент замедления: {self.simulation.mean_speed:.2f}")

        lines.append("=== Загрузка ресурсов ===")
        for name, utilization in self.simulation.utilization.items():
            lines.append(f"{name}: {utilization:.2f}")

        return "\n".join(lines)
