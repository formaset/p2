"""Модуль имитационного моделирования."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List

from .data_models import ExecutionPlan, ScheduledOperation


@dataclass
class SimulationResult:
    """Метрики работы производственной программы."""

    total_cost: float
    mean_risk: float
    mean_speed: float
    utilization: Dict[str, float]


class SimulationModel:
    """Простая модель, оценивающая отклонения от плана."""

    def __init__(self, plan: ExecutionPlan) -> None:
        self.plan = plan

    def _simulate_deviation(self, operation: ScheduledOperation) -> float:
        """Имитация сбоев с учётом риска."""
        noise = random.uniform(-0.15, 0.25)
        return max(0.0, 1.0 + noise * operation.task.risk)

    def run(self) -> SimulationResult:
        speed_losses: List[float] = []
        risks: List[float] = []
        total_cost = 0.0

        load = self.plan.total_load()
        max_load = max(load.values()) if load else 1
        utilization = {key: value / max_load for key, value in load.items()}

        for operation in self.plan.operations:
            deviation = self._simulate_deviation(operation)
            metrics = operation.compute_metrics()
            total_cost += metrics["cost"] * deviation
            speed_losses.append(deviation)
            risks.append(metrics["risk_percent"])

        mean_risk = sum(risks) / len(risks) if risks else 0.0
        mean_speed = sum(speed_losses) / len(speed_losses) if speed_losses else 1.0

        return SimulationResult(
            total_cost=total_cost,
            mean_risk=mean_risk,
            mean_speed=mean_speed,
            utilization=utilization,
        )
