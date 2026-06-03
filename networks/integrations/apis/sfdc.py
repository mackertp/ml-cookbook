"""
Connects into any Salesforce enviornment via REST API using the simple-salesforce library.
This utiliy file provides a custom class and functions to query, structure, and analyze data 
from Salesforce.

@author Preston Mackert
"""

# ------------------------------------------------------------------------------------------------------- #
# libraries
# ------------------------------------------------------------------------------------------------------- #

import os
import collections
import inspect
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from simple_salesforce import Salesforce as sf
from matplotlib.ticker import FuncFormatter
# load the environment variables from the .env file in the root of the project
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[3] / '.env')

# ------------------------------------------------------------------------------------------------------- #
# create a reusable, authenticated connection that can be called in notebooks
# ------------------------------------------------------------------------------------------------------- #

class SalesforceConnection(sf):
    """
    OAuth 2.0 client-credentials session via a connected app.
    Requires consumer key, secret, and personal salesforce domain from setup.
    """
    def __init__(self):
        """
        Creates a subclass to authenticate using .env file's defined credentials.
        """
        super().__init__(
            consumer_key=os.environ['sfdc_consumer_key'].strip(),
            consumer_secret=os.environ['sfdc_consumer_secret'].strip(),
            domain=os.environ['sfdc_domain'].strip()
        )

    @staticmethod
    def _clean_records(records):
        """
        Parse queried records into a pandas DataFrame
        """
        cleaned_records = []
        for record in records:
            clean_record = {}
            for key in record.keys():
                if key != 'attributes':
                    if record[key] is None:
                        if key == 'Opportunities':
                            clean_record['ClosedWonAmount'] = 0
                        elif key == 'Cases':
                            clean_record['CaseCount'] = 0
                    elif type(record[key]) is not collections.OrderedDict:
                        clean_record[key] = record[key]
                    else:
                        relationship_query = record[key]
                        if 'records' in relationship_query:
                            if key == 'Opportunities':
                                amounts = [
                                    row.get('Amount') for row in relationship_query['records']
                                    if row.get('Amount') is not None
                                ]
                                clean_record['ClosedWonAmount'] = sum(amounts) if amounts else 0
                            elif key == 'Cases':
                                clean_record['CaseCount'] = relationship_query.get('totalSize', 0)
                        else:
                            try:
                                for item in relationship_query:
                                    if type(relationship_query[item]) is not collections.OrderedDict:
                                        clean_record[key] = relationship_query[item]
                            except Exception:
                                clean_record[key] = 'unoptimized query, further analysis required'
            cleaned_records.append(clean_record)
        return pd.DataFrame(cleaned_records)

    @staticmethod
    def _format_list(thelist):
        """
        Support function to format a python list into a SOQL executable string for an IN clause.
        """
        list_string = '('
        for item in thelist[:-1]:
            list_string += "'" + str(item) + "'" + ', '
        list_string += "'" + str(thelist[-1]) + "'" + ')'
        return list_string

    @staticmethod
    def _library_query_call():
        """
        Returns chain of function calls to the Salesforce API so that the query() function can be 
        called internally by query_all.
        """
        for frame in inspect.stack()[1:]:
            if frame.function in ('query_all_iter', 'query_all', 'query_more'):
                return True
        return False

    def query(self, query, include_deleted=False, **kwargs):
        """
        Run SOQL and return a cleaned pandas DataFrame.
        Delegates to the parent query() when called internally by query_all.
        """
        if kwargs or self._library_query_call():
            return super().query(query, include_deleted=include_deleted, **kwargs)
        data = super().query_all(query, include_deleted=include_deleted)
        return self._clean_records(data['records'])

    def query_list(self, soql, thelist):
        """
        Run SOQL with an IN clause built from a Python list of ids.
        """
        soql += self._format_list(thelist)
        data = super().query_all(soql)
        return self._clean_records(data['records'])


# ------------------------------------------------------------------------------------------------------- #
# visualization functions (specific analysis) ~ https://www.youtube.com/watch?v=HvnvvIQbWuw
# ------------------------------------------------------------------------------------------------------- #

def _dollar_ticks(value, _position):
    if value >= 1e9:
        return f'${value / 1e9:.1f}B'
    if value >= 1e6:
        return f'${value / 1e6:.1f}M'
    if value >= 1e3:
        return f'${value / 1e3:.0f}K'
    return f'${value:,.0f}'


def plot_avg_revenue_by_industry(accounts, ax=None):
    """
    Bar chart comparing average Annual Revenue by Industry from an accounts DataFrame.
    """
    revenue_by_industry = (
        accounts.dropna(subset=['Industry', 'AnnualRevenue'])
        .groupby('Industry', as_index=False)['AnnualRevenue']
        .mean()
        .sort_values('AnnualRevenue', ascending=False)
    )
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 6))
    ax.bar(
        revenue_by_industry['Industry'],
        revenue_by_industry['AnnualRevenue'],
        color='#0c5c00',
        edgecolor='#1F1F1F',
    )
    ax.set_title('Avg. Annual Revenue by Account Industry')
    ax.set_xlabel('Industry')
    ax.set_ylabel('Average Annual Revenue')
    ax.yaxis.set_major_formatter(FuncFormatter(_dollar_ticks))
    ax.tick_params(axis='x', rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.show()


def plot_top_closed_won(accounts, industry, top_n=5, ax=None):
    """
    Horizontal bar chart of the top energy accounts by ClosedWonAmount.
    """
    top_accts = (
        accounts.loc[accounts['Industry'] == industry, ['Name', 'ClosedWonAmount']]
        .nlargest(top_n, 'ClosedWonAmount')
        .sort_values('ClosedWonAmount', ascending=True)
    )
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 5))
    ax.barh(
        top_accts['Name'],
        top_accts['ClosedWonAmount'],
        color='#0c5c00',
        edgecolor='#1F1F1F',
    )
    ax.set_title(f'Top {len(top_accts)} {industry} Accounts by Closed Opportunity Value ($)')
    ax.set_xlabel('Closed Won Amount')
    ax.set_ylabel('Account')
    ax.xaxis.set_major_formatter(FuncFormatter(_dollar_ticks))
    ax.grid(axis='x', linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.show()
