import pandas as pd
import plotly.graph_objects as go
import ipywidgets as widgets
from IPython.display import display

def plot_time_series(df, uid_col, date_col = 'ds', y_col = 'y'):
    """
    This function generates an interactive Plotly time-series visualization with a searchable
    dropdown menu, allowing the user to select and display any time-series in the dataframe
    by searching for its unique_id. The plot and widgets are rendered inline in a Jupyter notebook.

    Input:
    - df (pandas DataFrame): Dataframe containing the time-series data with the following columns:
    - uid_col (str): Name of your unique_id column
    - date_col (str): Name of your date column
    - y_col (str): Name of your target column

    Output:
    - Displays an interactive ipywidgets layout containing:
        - search_box: Text input to filter the dropdown options by unique_id.
        - dropdown: Dropdown menu to select the time-series to display.
        - fig_widget: Plotly FigureWidget rendering the selected time-series.
    """

    # Extract the list of all unique time-series IDs from the dataframe.
    unique_ids = list(df[uid_col].unique())

    # --- Widgets ---

    # Text input widget for searching/filtering the dropdown options.
    search_box = widgets.Text(
        placeholder="Search time-series ID...",
        description="Search:",
        layout=widgets.Layout(width="300px")
    )

    # Dropdown widget for selecting a specific time-series to display.
    dropdown = widgets.Dropdown(
        options=unique_ids,
        value=unique_ids[0],
        description="Series:",
        layout=widgets.Layout(width="300px")
    )

    # FigureWidget is a Plotly figure that integrates with ipywidgets, allowing
    # its data and layout to be updated dynamically without re-rendering the entire figure.
    fig_widget = go.FigureWidget()

    def get_series(uid):
        """
        Helper function that retrieves and sorts the data for a given unique_id.

        Input:
        - uid: The unique_id of the time-series to retrieve.

        Output:
        - Tuple (ds, y) containing the date and target value columns of the selected time-series,
          sorted in ascending date order to ensure lines are drawn correctly.
        """
        # Filter the dataframe to only the rows matching the given uid, then sort by date.
        subset = df[df[uid_col] == uid].sort_values(date_col)
        return subset[date_col], subset[y_col]

    # Retrieve the data for the first time-series to initialize the figure.
    x0, y0 = get_series(unique_ids[0])

    # Add the initial time-series as a scatter (line) trace to the figure.
    # This trace will be mutated in-place on subsequent selections rather than
    # adding/removing traces, which is more efficient.
    fig_widget.add_scatter(x=x0, y=y0, mode="lines", name=str(unique_ids[0]))

    # Set the initial layout of the figure: title, axis labels, and dimensions.
    fig_widget.update_layout(
        title=f"Time Series: {unique_ids[0]}",
        xaxis_title="Date",
        yaxis_title="Value",
        height=600,
        width=1100
    )

    def on_search(change):
        """
        Callback triggered whenever the text in search_box changes.
        Filters the dropdown options to only show unique_ids that contain
        the search query as a substring (case-insensitive).

        Input:
        - change (dict): Dictionary provided by the ipywidgets observe mechanism.
                         change["new"] holds the current value of the search box.
        """
        # Retrieve the current search query in lowercase for case-insensitive matching.
        query = change["new"].lower()

        # Filter unique_ids to those containing the query as a substring.
        # If no matches are found, fall back to showing all unique_ids.
        filtered = [uid for uid in unique_ids if query in str(uid).lower()]
        dropdown.options = filtered if filtered else unique_ids

        # Automatically select the first result in the filtered list,
        # which in turn triggers on_select to update the plot.
        if filtered:
            dropdown.value = filtered[0]

    def on_select(change):
        """
        Callback triggered whenever the selected value in the dropdown changes.
        Updates the figure's trace data and title to reflect the newly selected time-series.

        Input:
        - change (dict): Dictionary provided by the ipywidgets observe mechanism.
                         change["new"] holds the currently selected unique_id.
        """
        # Retrieve the unique_id of the newly selected time-series.
        uid = change["new"]
        x, y = get_series(uid)

        # batch_update() groups all mutations to the figure into a single atomic update,
        # preventing intermediate render states and avoiding visual flickering.
        with fig_widget.batch_update():
            # Update the x and y data of the existing trace in-place.
            fig_widget.data[0].x = x
            fig_widget.data[0].y = y
            # Update the legend label of the trace to the new unique_id.
            fig_widget.data[0].name = str(uid)
            # Update the figure title to reflect the currently displayed time-series.
            fig_widget.layout.title.text = f"Time Series: {uid}"

    # Register on_search as the callback for any change to the search box value.
    # names="value" ensures only changes to the text content trigger the callback.
    search_box.observe(on_search, names="value")

    # Register on_select as the callback for any change to the dropdown selection.
    dropdown.observe(on_select, names="value")

    # Arrange and display the widgets:
    # - HBox places the search_box and dropdown side by side horizontally.
    # - VBox stacks the HBox control bar above the figure vertically.
    display(widgets.VBox([
        widgets.HBox(
            [search_box, dropdown],
        ),
        fig_widget
    ]))