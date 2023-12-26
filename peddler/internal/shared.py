import configparser, logging

import mysql.connector

logger = logging.getLogger(__name__)


class DabaseManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.parser = configparser.ConfigParser()
        self.parser.read(config_path)

        try:
            self.world = self.parser["DB"]["world_database"]
            self.player = self.parser["DB"]["player_database"]
        except Exception as e:
            logger.error(f"Error: {e}")

        self.world_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="world_pool",
            pool_size=10,
            host=self.parser["DB"]["db_host"],
            user=self.parser["DB"]["db_username"],
            password=self.parser["DB"]["db_password"],
            database=self.parser["DB"]["world_database"],
        )

        self.player_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="player_pool",
            pool_size=10,
            host=self.parser["DB"]["db_host"],
            user=self.parser["DB"]["db_username"],
            password=self.parser["DB"]["db_password"],
            database=self.parser["DB"]["player_database"],
        )

        self.realmdb_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="realmdb_pool",
            pool_size=10,
            host=self.parser["DB"]["db_host"],
            user=self.parser["DB"]["db_username"],
            password=self.parser["DB"]["db_password"],
            database=self.parser["DB"]["realm_database"],
        )

        self.table_names = ["item_template", "creature_template"]

    def get_connection(
        self, database: str
    ) -> mysql.connector.pooling.PooledMySQLConnection:
        """
        Get a connection from the pool.

        Returns:
            MySQLConnection: A connection to the database.
        """

        if database == "world":
            return self.world_pool.get_connection()
        elif database == "player":
            return self.player_pool.get_connection()
        else:
            raise ValueError("Invalid database type specified")

    def get_single(
        self, key: str, value: str, database_type: str, table_name: str
    ) -> dict:
        """
        Get a single row from the database.

        Args:
            key (str): The column name to search.
            value (str): The value to search for.
            database_type (str): The type of database ('world' or 'player').
            table_name (str): The name of the table to search.

        Returns:
            dict: A dictionary containing the row data.
        """

        with self.get_connection(database_type) as connection:
            cursor = connection.cursor(dictionary=True)
            query = f"SELECT * FROM {table_name} WHERE {key} = %s LIMIT 1"
            cursor.execute(query, (value,))
            result = cursor.fetchone()
        return result

    def get_multiple(
        self, key: str, value: str, database_type: str, table_name: str
    ) -> dict:
        """
        Get multiple rows from the database.

        Args:
            key (str): The column name to search.
            value (str): The value to search for.
            database_type (str): The type of database ('world' or 'player').
            table_name (str): The name of the table to search.

        Returns:
            dict: A dictionary containing the row data.
        """

        with self.get_connection(database_type) as connection:
            cursor = connection.cursor(dictionary=True)
            query = f"SELECT * FROM {table_name} WHERE {key} = %s"
            cursor.execute(query, (value,))
            result = cursor.fetchall()
        return result

    def update_single_field(
        self,
        search_key: str,
        search_value: str,
        update_key: str,
        update_value: str,
        database_type: str,
        table_name: str,
    ) -> bool:
        """
        Update a single field in a single row.

        Args:
            search_key (str): The column name to search.
            search_value (str): The value to search for.
            update_key (str): The column name to update.
            update_value (str): The value to update to.
            database_type (str): The type of database ('world' or 'player').
            table_name (str): The name of the table to search.

        Returns:
            bool: True if the entry was successfully updated, False otherwise.
        """

        with self.get_connection(database_type) as connection:
            cursor = connection.cursor()
            query = f"UPDATE {table_name} SET {update_key} = %s WHERE {search_key} = %s"
            cursor.execute(query, (update_value, search_value))
            connection.commit()
            success = cursor.rowcount > 0
        return success

    def add_entry(self, database_type: str, table_name: str, **kwargs) -> bool:
        """
        Add an entry to the database.

        Args:
            database_type (str): The type of database ('world' or 'player').
            table_name (str): The name of the table to add to.

        Returns:
            bool: True if the entry was successfully added, False otherwise.
        """

        with self.get_connection(database_type) as connection:
            cursor = connection.cursor()
            columns = ", ".join(kwargs.keys())
            placeholders = ", ".join(["%s"] * len(kwargs))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, tuple(kwargs.values()))
            connection.commit()
            success = cursor.rowcount > 0
        return success

    def ensure_table_exists(
        self, database_type: str, table_name: str, table_schema: str
    ):
        """
        Ensure that the specified table exists in the database, creating it if it does not.

        Args:
            database_type (str): The type of database ('world' or 'player').
            table_name (str): The name of the table to check and/or create.
            table_schema (str): The SQL schema for the table, used to create it if missing.

        Returns:
            bool: True if the table exists or was successfully created, False otherwise.
        """

        with self.get_connection(database_type) as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(f"SHOW TABLES LIKE %s", (table_name,))
                    result = cursor.fetchone()
                    if not result:
                        cursor.execute(table_schema)
                        connection.commit()
                except Exception as e:
                    logger.error(f"Error checking/creating table {table_name}: {e}")
                    connection.rollback()
                    return False
        return True
