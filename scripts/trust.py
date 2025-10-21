from upsetplot import from_memberships
from upsetplot import plot
from matplotlib import pyplot
import matplotlib
from itertools import combinations

import numpy as np
import os
import pandas as pd
from collections import Counter
from matplotlib import pyplot as plt
from matplotlib.offsetbox import AnchoredText
from matplotlib.ticker import MaxNLocator

inputFolder = './data'
outputFolder = './output'
data = pd.read_excel(f'{inputFolder}/data-extracted.xlsx')
column = 'Sus. dimensions'

columnFilename = {
    'Sus. dimensions' : 'sustainability_dim'
}
def create_bar_chart_from_file(file_path, x_column, y_column, title, x_label, y_label, output_filename="trust.pdf"):
    """
    Creates a bar chart from a specified file using Pandas and Matplotlib.

    Args:
        file_path (str): The path to the data file (e.g., 'data.csv', 'data.xlsx').
        x_column (str): The name of the column to use for the x-axis.
        y_column (str): The name of the column to use for the y-axis.
        title (str): The title of the bar chart.
        x_label (str): The label for the x-axis.
        y_label (str): The label for the y-axis.
        output_filename (str): The name of the file to save the chart as.
    """
    try:
        # Determine file type and read accordingly
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            print("Unsupported file format. Please provide a .csv or .xlsx file.")
            return

        # Create the bar chart
        plt.figure(figsize=(10, 6)) # Adjust figure size as needed
        plt.bar(df[x_column], df[y_column])

        # Add labels and title
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.xticks(rotation=45, ha='right') # Rotate x-axis labels if they are long
        plt.tight_layout() # Adjust layout to prevent labels from overlapping

        # Save the chart
        plt.savefig(output_filename)
        print(f"Bar chart saved successfully as {output_filename}")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except KeyError as e:
        print(f"Error: Column '{e}' not found in the file. Please check column names.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Example usage:
    # Create a dummy CSV file for demonstration
    dummy_data = {
        'Category': ['A', 'B', 'C', 'D', 'E'],
        'Value': [10, 25, 15, 30, 20]
    }
    dummy_df = pd.DataFrame(dummy_data)
    dummy_df.to_csv('sample_data.csv', index=False)

    # Call the function with your file details
    create_bar_chart_from_file(
        file_path='sample_data.csv',
        x_column='Category',
        y_column='Value',
        title='Sample Bar Chart of Categories',
        x_label='Category',
        y_label='Value',
        output_filename='sample_bar_chart.png'
    )
