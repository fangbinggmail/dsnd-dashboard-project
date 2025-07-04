# Import any dependencies needed to execute sql queries
import pandas as pd  # noqa: F401
import numpy as np  # noqa: F401
import random, pickle, json  # noqa: E401, F401
from sqlite3 import connect  # noqa: F401
from datetime import timedelta, date  # noqa: F401
from employee_events.sql_execution import QueryMixin


# Define a class called QueryBase
# Use inheritance to add methods
# for querying the employee_events database.
# Need the QueryMixin to execute SQL queries for notes and event_counts
class QueryBase(QueryMixin):

    # Create a class attribute called `name`
    # set the attribute to an empty string
    name = ''

    # Define a `names` method that receives
    # no passed arguments
    def names(self):

        # Return an empty list
        return []

    def model_data(self, id):
        raise NotImplementedError(
            "The model_data method must be implemented in the subclass."
        )

    # Define an `event_counts` method
    # that receives an `id` argument
    # This method should return a pandas dataframe
    def event_counts(self, id):

        # QUERY 1
        # Write an SQL query that groups by `event_date`
        # and sums the number of positive and negative events
        # Use f-string formatting to set the FROM {table}
        # to the `name` class attribute
        # Use f-string formatting to set the name
        # of id columns used for joining
        # order by the event_date column
        table = 'employee_events'
        query = f"""
            SELECT event_date
                 , SUM(positive_events) AS positive_events
                 , SUM(negative_events) AS negative_events
            FROM {table}
            WHERE {self.name}_id = {id}
            GROUP BY event_date
            ORDER BY event_date;
        """

        # Return the result of the pandas_query method
        return self.pandas_query(query)

    # Define a `notes` method that receives an id argument
    # This function should return a pandas dataframe
    def notes(self, id):

        # QUERY 2
        # Write an SQL query that returns `note_date`, and `note`
        # from the `notes` table
        # Set the joined table names and id columns
        # with f-string formatting
        # so the query returns the notes
        # for the table name in the `name` class attribute
        query = f"""
            SELECT note_date, note
            FROM notes
            WHERE {self.name}_id = {id}
            ORDER BY note_date;
        """

        # Return the result of the pandas_query method
        return self.pandas_query(query)
