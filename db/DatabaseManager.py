# Manages facts database
import os
import random
import sqlite3
from collections import defaultdict
from typing import List, Dict

from kivy import Logger


class DatabaseManager:
    def __init__(self):
        # Key is product name, then a list of facts about that product
        self.loaded_facts: Dict[str, List[str]] = defaultdict(list)
        self.connection = None

    def create_static_database(self):
        # Connect to the database and return database connection object
        conn = None

        Logger.debug(f"StellaPayUI: Creating static fun fact database")

        # Create all tables and add the the database file
        try:
            conn = sqlite3.connect('db/static_fun_fact_database.db')

            # # SQLite command to create table with two fields, namely product and fun_fact
            static_fun_facts_table = "CREATE TABLE IF NOT EXISTS static_fun_facts(" \
                                     "product text NOT NULL, " \
                                     "fun_fact text PRIMARY KEY " \
                                     ");"
            #
            # one_day_fun_fact_table = "CREATE TABLE IF NOT EXISTS one_day_fun_fact(" \
            #                          "product text PRIMARY KEY " \
            #                          "fun_fact text PRIMARY KEY " \
            #                          ");"
            #
            # one_week_fun_fact_table = "CREATE TABLE IF NOT EXISTS one_week_fun_fact(" \
            #                           "product text PRIMARY KEY " \
            #                           "fun_fact text PRIMARY KEY " \
            #                           ");"
            #
            # one_month_fun_fact_table = "CREATE TABLE IF NOT EXISTS one_month_fun_fact(" \
            #                            "product text PRIMARY KEY " \
            #                            "fun_fact text PRIMARY KEY " \
            #                            ");"
            #

            # Create connection to the database and add the tables
            db_conn = conn.cursor()
            db_conn.execute(static_fun_facts_table)
            # db_conn.execute(one_day_fun_fact_table)
            # db_conn.execute(one_week_fun_fact_table)
            # db_conn.execute(one_month_fun_fact_table)

        except sqlite3.Error as e:
            Logger.critical("StellaPayUI: " + e)
            os._exit(1)

        self.connection = conn

    def load_facts_database(self):
        Logger.debug(f"StellaPayUI: Loading fun fact database")

        cursor = self.connection.cursor()

        cursor.execute("SELECT product, fun_fact FROM static_fun_facts")

        fun_facts = cursor.fetchall()

        count = 0

        for item in fun_facts:
            product = item[0]
            fun_fact = item[1]

            self.loaded_facts[product].append(fun_fact)

            count += 1

        Logger.debug(f"StellaPayUI: Loaded {count} fun facts from the database")

    def get_random_fun_fact(self, product_name: str):
        # If we don't have any fun facts about this product, return a default string.
        fun_facts = []

        for item_name, fun_fact in self.loaded_facts.items():
            # Check to see if the product name is contained in the product name
            if item_name.lower().strip() in product_name.lower().strip():
                # If so, we want to choose it.
                fun_facts.extend(fun_fact)

        # If we found no fun facts.
        if len(fun_facts) == 0:
            fun_facts.append("Ik kon hier geen leuk feitje over vinden")

        # Choose a random one
        return random.choice(fun_facts)
