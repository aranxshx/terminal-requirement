from __future__ import annotations

from lib.catalog import ApplianceCatalog
from lib.models import ApplianceRecord
from lib.repository import HouseholdRecordRepository
from lib.services import BudgetService, EnergyComputationService, RankingService


class WattzUpApplicationService:
    """Coordinates user session, records, persistence, and reporting behaviors."""

    def __init__(
        self,
        repository: HouseholdRecordRepository,
        catalog: ApplianceCatalog,
        computation_service: EnergyComputationService,
        ranking_service: RankingService,
        budget_service: BudgetService,
    ) -> None:
        self._repository = repository
        self._catalog = catalog
        self._computation_service = computation_service
        self._ranking_service = ranking_service
        self._budget_service = budget_service

        self.current_username: str | None = None
        self.records: list[ApplianceRecord] = []
        self.budget: float | None = None

    @property
    def catalog(self) -> ApplianceCatalog:
        return self._catalog

    def list_existing_users(self) -> list[str]:
        return self._repository.list_usernames()

    def create_new_user_session(self, username: str) -> str:
        safe_username = self._repository.sanitize_username(username)
        if not safe_username:
            raise ValueError("Username must include letters or numbers.")
        if self._repository.username_exists(safe_username):
            raise ValueError("That username already exists.")

        self.current_username = safe_username
        self.records = []
        self.budget = None
        return safe_username

    def continue_user_session(self, username: str) -> str:
        safe_username = self._repository.sanitize_username(username)
        if not safe_username:
            raise ValueError("Invalid username.")

        self.current_username = safe_username
        self.records = self._repository.load_for_user(safe_username)
        self.budget = None
        return safe_username

    def add_appliance_usage(self, room: str, appliance: str, usage_level: str) -> ApplianceRecord:
        wattage = self._catalog.wattage_for(room, appliance)
        record = self._computation_service.build_record(room, appliance, wattage, usage_level)
        self.records.append(record)
        self.save_current_session()
        return record

    def save_current_session(self) -> None:
        if self.current_username is None:
            raise RuntimeError("No active user session.")
        self._repository.save_for_user(self.current_username, self.records)

    def load_current_session(self) -> None:
        if self.current_username is None:
            raise RuntimeError("No active user session.")
        self.records = self._repository.load_for_user(self.current_username)

    def clear_records(self) -> None:
        self.records = []

    def set_budget(self, budget: float | None) -> None:
        if budget is not None and budget < 0:
            raise ValueError("Budget cannot be negative.")
        self.budget = budget

    def total_cost(self) -> float:
        return self._computation_service.total_cost(self.records)

    def budget_status(self) -> str:
        return self._budget_service.budget_status(self.total_cost(), self.budget)

    def ranked_appliances(self) -> list[ApplianceRecord]:
        return self._ranking_service.rank_appliances(self.records)

    def ranked_rooms(self) -> list[tuple[str, float]]:
        return self._ranking_service.rank_rooms(self.records)


def create_default_application_service() -> WattzUpApplicationService:
    """Create the standard application service with production configuration."""
    return WattzUpApplicationService(
        repository=HouseholdRecordRepository(),
        catalog=ApplianceCatalog(),
        computation_service=EnergyComputationService(),
        ranking_service=RankingService(),
        budget_service=BudgetService(),
    )
