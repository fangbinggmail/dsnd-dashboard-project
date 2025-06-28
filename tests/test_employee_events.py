import pytest
import pandas as pd
from pathlib import Path

# Using pathlib create a project_root
# variable set to the absolute path
# for the root of this project
project_root = Path(__file__).resolve().parent.parent


# apply the pytest fixture decorator
# to a `db_path` function
@pytest.fixture
def db_path():

    # Using the `project_root` variable
    # return a pathlib object for the `employee_events.db` file
    db_file = project_root / 'python-package'
    db_file = db_file / 'employee_events' / 'employee_events.db'

    return db_file


# Define a function called
# `test_db_exists`
# This function should receive an argument
# with the same name as the function
# the creates the "fixture" for
# the database's filepath
def test_db_exists(db_path):

    # using the pathlib `.is_file` method
    # assert that the sqlite database file exists
    # at the location passed to the test_db_exists function
    assert db_path.is_file(), f"Database file does not exist at {db_path}"


@pytest.fixture
def db_conn(db_path):
    from sqlite3 import connect
    return connect(db_path)


@pytest.fixture
def table_names(db_conn):
    name_tuples = db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()
    return [x[0] for x in name_tuples]


# Define a test fixture for employee ids
@pytest.fixture
def employee_ids(db_conn):
    # Execute a query to get all employee ids
    query = "SELECT employee_id FROM employee;"
    result = db_conn.execute(query).fetchall()

    # Return a list of employee ids
    return [row[0] for row in result]


# define a test fixture for event_counts for employee with id 1
@pytest.fixture
def employee_event_counts(db_conn):
    # Execute a query to get event counts for employee with id 1
    query = """
        SELECT event_date, SUM(positive_events) AS positive_events,
        SUM(negative_events) AS negative_events
        FROM employee_events
        WHERE employee_id = 1
        GROUP BY event_date
        ORDER BY event_date;
    """
    result = db_conn.execute(query).fetchall()

    # Return a list of tuples with event counts
    return [(row[0], row[1], row[2]) for row in result]


# Define test fixtures for the team notes
@pytest.fixture
def team_notes(db_conn):
    # Execute a query to get all team notes
    query = """
        SELECT note_date, note
        FROM notes
        WHERE team_id = 1
        ORDER BY note_date;
    """
    result = db_conn.execute(query).fetchall()

    # Return a list of tuples with note date and note text
    return [(row[0], row[1]) for row in result]


# Define a test function called
# `test_employee_table_exists`
# This function should receive the `table_names`
# fixture as an argument
def test_employee_table_exists(table_names):

    # Assert that the string 'employee'
    # is in the table_names list
    assert 'employee' in table_names, "The 'employee' table does not exist in the database."  # noqa: E501


# Define a test function called
# `test_team_table_exists`
# This function should receive the `table_names`
# fixture as an argument
def test_team_table_exists(table_names):

    # Assert that the string 'team'
    # is in the table_names list
    assert 'team' in table_names, "The 'team' table does not exist in the database."  # noqa: E501


# Define a test function called
# `test_employee_events_table_exists`
# This function should receive the `table_names`
# fixture as an argument
def test_employee_events_table_exists(table_names):

    # Assert that the string 'employee_events'
    # is in the table_names list
    assert 'employee_events' in table_names, "The 'employee_events' table does not exist in the database."  # noqa: E501


# Define a test function called
# `test_employee_ids`
# This function should receive the `db_conn`
# fixture as an argument
def test_employee_ids(db_conn, employee_ids):

    # Execute a query to get all employee ids
    query = "SELECT employee_id FROM employee;"
    result = db_conn.execute(query).fetchall()

    print("Employee IDs from the database:", result)

    # Assert that the number of employee ids
    # returned by the query is equal to the length
    # of the employee_ids fixture
    assert len(result) == len(employee_ids), "The number of employee ids does not match the expected count."  # noqa: E501

    # Assert that all employee ids in the result
    # are in the employee_ids fixture
    for row in result:
        assert row[0] in employee_ids, f"Employee id {row[0]} not found in employee_ids fixture."  # noqa: E501


# Define a test function called
# `test_event_counts` for Employee with id 1
# This function should instantiate the Employee class
# and call the `event_counts` method
# with the id 1
def test_employee_event_counts(db_conn, employee_event_counts):
    from employee_events.employee import Employee

    print(employee_event_counts)

    # Create an instance of the Employee class
    employee = Employee()

    # Call the event_counts method with id 1

    result = employee.event_counts(1)
    print("Event counts for employee with id 1:\n", result)

    # Assert that the result is a pandas DataFrame
    assert isinstance(result, pd.DataFrame), "The result is not a pandas DataFrame."  # noqa: E501

    # Assert that the number of rows in the result matches the length of
    # event_counts fixture
    assert len(result) == len(employee_event_counts), "The number of rows in the result does not match the expected count."  # noqa: E501

    # Assert that the data in the result matches the event_counts fixture
    for idx, row in enumerate(result.itertuples(index=False)):
        assert (row.event_date, row.positive_events, row.negative_events) == employee_event_counts[idx], f"Row {idx} does not match expected values."  # noqa: E501


# Define a test function for team notes
def test_team_notes(db_conn, team_notes):
    from employee_events.team import Team

    # Create an instance of the Team class
    team = Team()

    # Call the notes method with id 1
    result = team.notes(1)
    print("Team notes for team with id 1:\n", result)

    # Assert that the result is a pandas DataFrame
    assert isinstance(result, pd.DataFrame), "The result is not a pandas DataFrame."  # noqa: E501

    # Assert that the number of rows in the result matches the length of
    # team_notes fixture
    assert len(result) == len(team_notes), "The number of rows in the result does not match the expected count."  # noqa: E501

    # Assert that the data in the result matches the team_notes fixture
    for idx, row in enumerate(result.itertuples(index=False)):
        assert (row.note_date, row.note) == team_notes[idx], f"Row {idx} does not match expected values."  # noqa: E501
