import logging

from peddler.internal.shared import DabaseManager
from peddler.internal.schema import BOT_AH_TABLE_SCHEMA

logger = logging.getLogger(__name__)


class PeddlerProcessor(DabaseManager):
    def __init__(self, config_path: str):
        super().__init__(config_path)

        if not self.ensure_table_exists(
            "player", "ah_bot_accounts", BOT_AH_TABLE_SCHEMA
        ):
            raise Exception("Failed to create table ah_bot_accounts")

    def get_all_bots(self) -> list:
        """
        Retrieve all bot accounts from the database.

        Returns:
            List[Dict]: A list of dictionaries, each representing a bot account.
        """

        return self.get_multiple(
            key="bot_account_id",
            value="%",
            database_type="player",
            table_name="ah_bot_accounts",
        )
