from fasthtml.common import *  # type: ignore # noqa: F401, F403, E261
import matplotlib.pyplot as plt
import numpy as np

# Import QueryBase, Employee, Team from employee_events
from employee_events import QueryBase, Employee, Team

# import the load_model function from the utils.py file
from utils import load_model  # type: ignore

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
    )

from combined_components import FormGroup, CombinedComponent


# Create a subclass of base_components/dropdown
# called `ReportDropdown`
class ReportDropdown(Dropdown):

    # Overwrite the build_component method
    # ensuring it has the same parameters
    # as the Report parent class's method
    def build_component(
        self,
        entity_id,
        model: QueryBase,
        **kwargs
    ):
        #  Set the `label` attribute so it is set
        #  to the `name` attribute for the model
        self.label = model.name

        # Return the output from the
        # parent class's build_component method
        return super().build_component(entity_id, model, **kwargs)

    # Overwrite the `component_data` method
    # Ensure the method uses the same parameters
    # as the parent class method
    def component_data(
        self,
        entity_id,
        model: QueryBase,
        **kwargs
    ):
        # Using the model argument
        # call the employee_events method
        # that returns the user-type's
        # names and ids
        data = model.names()

        # Return a list of tuples
        # containing the name and id
        return [(name, id) for name, id in data]


# Create a subclass of base_components/BaseComponent
# called `Header`
class Header(BaseComponent):

    # Overwrite the `build_component` method
    # Ensure the method has the same parameters
    # as the parent class
    def build_component(
        self,
        entity_id,
        model: QueryBase,
        **kwargs
    ):

        # Using the model argument for this method
        # return a fasthtml H1 objects
        # containing the model's name attribute
        return H1(model.name, cls='header', **kwargs)  # noqa: F405


# Create a subclass of base_components/MatplotlibViz
# called `LineChart`
class LineChart(MatplotlibViz):

    # Overwrite the parent class's `visualization`
    # method. Use the same parameters as the parent
    def visualization(self, entity_id: int, model: QueryBase, **kwargs):

        # Pass the `asset_id` argument to
        # the model's `event_counts` method to
        # receive the x (Day) and y (event count)
        event_counts = model.event_counts(entity_id)

        # Use the pandas .fillna method to fill nulls with 0
        event_counts = event_counts.fillna(0)

        # User the pandas .set_index method to set
        # the date column as the index
        event_counts = event_counts.set_index('event_date')

        # Sort the index
        event_counts = event_counts.sort_index()

        # Use the .cumsum method to change the data
        # in the dataframe to cumulative counts
        cumulative_counts = event_counts.cumsum()

        # Set the dataframe columns to the list
        # ['Positive', 'Negative']
        cumulative_counts = cumulative_counts.rename(
            columns={
                'positive_events': 'Positive',
                'negative_events': 'Negative'
            }
        )

        # Initialize a matplotlib figure and axis
        # using the `plt.subplots` method
        # Set the figure size to 10 by 5 inches

        # Initialize a pandas subplot
        # and assign the figure and axis
        # to variables
        fig, ax = plt.subplots(figsize=(10, 5))

        # call the .plot method for the
        # cumulative counts dataframe
        cumulative_counts.plot(ax=ax, kind='line')

        # pass the axis variable
        # to the `.set_axis_styling`
        # method
        # Use keyword arguments to set
        # the border color and font color to black.
        # Reference the base_components/matplotlib_viz file
        # to inspect the supported keyword arguments
        self.set_axis_styling(ax)

        # Set title and labels for x and y axis
        ax.set_title('Cumulative Event Counts')
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Count')


# Create a subclass of base_components/MatplotlibViz
# called `BarChart`
class BarChart(MatplotlibViz):

    # Create a `predictor` class attribute
    # assign the attribute to the output
    # of the `load_model` utils function
    predictor = load_model()

    # Overwrite the parent class `visualization` method
    # Use the same parameters as the parent
    def visualization(self, entity_id: int, model: QueryBase, **kwargs):

        # Using the model and asset_id arguments
        # pass the `asset_id` to the `.model_data` method
        # to receive the data that can be passed to the machine
        # learning model
        data = model.model_data(entity_id)

        # Using the predictor class attribute
        # pass the data to the `predict_proba` method
        # to receive the model's prediction
        predict_proba = self.predictor.predict_proba(data)

        # Index the second column of predict_proba output
        # The shape should be (<number of records>, 1)

        # Below, create a `pred` variable set to
        # the number we want to visualize
        #
        # If the model's name attribute is "team"
        # We want to visualize the mean of the predict_proba output

        # Otherwise set `pred` to the first value
        # of the predict_proba output

        # We'll take the column wise mean of the predictions
        # to get the average prediction for the team
        # or employee. If Employee, there is only 1 row and mean of a
        # single number is the number itself.
        pred = np.mean(predict_proba, axis=0)[0]

        # Initialize a matplotlib subplot
        fig, ax = plt.subplots(figsize=(5, 2))

        # Run the following code unchanged
        ax.barh([''], [pred])
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)

        # pass the axis variable
        # to the `.set_axis_styling`
        # method
        self.set_axis_styling(ax)


# Create a subclass of combined_components/CombinedComponent
# called Visualizations
class Visualizations(CombinedComponent):

    # Set the `children`
    # class attribute to a list
    # containing an initialized
    # instance of `LineChart` and `BarChart`
    children = [
        LineChart(),
        BarChart()
    ]

    # Leave this line unchanged
    outer_div_type = Div(cls='grid')  # noqa: F405


# Create a subclass of base_components/DataTable
# called `NotesTable`
class NotesTable(DataTable):

    # Overwrite the `component_data` method
    # using the same parameters as the parent class
    def component_data(  # type: ignore
            self,
            entity_id: int,
            model: QueryBase,
            **kwargs):

        # Using the model and entity_id arguments
        # pass the entity_id to the model's .notes
        # method. Return the output
        return model.notes(entity_id)


class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
            ),
        ReportDropdown(
            id="selector",
            name="user-selection")
        ]


# Create a subclass of CombinedComponents
# called `Report`
class Report(CombinedComponent):

    # Set the `children`
    # class attribute to a list
    # containing initialized instances
    # of the header, dashboard filters,
    # data visualizations, and notes table
    children = [
        Header(),
        DashboardFilters(),
        Visualizations(),
        NotesTable()
    ]


# Initialize a fasthtml app
app = FastHTML()  # noqa: F405

# Initialize the `Report` class
report = Report()


# Create a route for a get request
# Set the route's path to the root
@app.get('/')  # type: ignore
def index():

    # Call the initialized report
    # pass the integer 1 and an instance
    # of the Employee class as arguments
    # Return the result
    return report(1, Employee())


# Create a route for a get request
# Set the route's path to receive a request
# for an employee ID so `/employee/2`
# will return the page for the employee with
# an ID of `2`.
# parameterize the employee ID
# to a string datatype
@app.get('/employee/{id:int}')  # type: ignore
def employee(r, id: int):

    # Call the initialized report
    # pass the ID and an instance
    # of the Employee SQL class as arguments
    # Return the result
    return report(id, Employee())


# Create a route for a get request
# Set the route's path to receive a request
# for a team ID so `/team/2`
# will return the page for the team with
# an ID of `2`.
# parameterize the team ID
# to a string datatype
@app.get('/team/{id:int}')  # type: ignore
def team(r, id: int):

    # Call the initialized report
    # pass the id and an instance
    # of the Team SQL class as arguments
    # Return the result
    return report(id, Team())


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')  # type: ignore
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')  # type: ignore
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)


serve()  # noqa: F405
