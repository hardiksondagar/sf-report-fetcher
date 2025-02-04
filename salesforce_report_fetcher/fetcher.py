import requests
import functools
from typing import Dict, List, Tuple, Optional
import urllib.parse


class SalesforceReportFetcher:
    """
    A class to handle Salesforce report fetching with automatic pagination.
    Handles both metadata retrieval and report execution with built-in pagination
    to overcome the 2000 row limit in Salesforce reports.
    """
    
    def __init__(self, access_token: str, instance_url: str, api_version: str = "57.0"):
        """
        Initialize the report fetcher.
        
        Args:
            access_token (str): Salesforce access token
            instance_url (str): Salesforce instance URL
            api_version (str): Salesforce API version (default: "57.0")
        """
        self.access_token = access_token
        self.instance_url = instance_url.rstrip('/')
        self.api_version = api_version.strip('v')  # Remove 'v' if present
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        self.base_api_path = f"/services/data/v{self.api_version}/analytics/reports"

    @functools.lru_cache(maxsize=8)
    def get_metadata(self, report_id: str) -> Dict:
        """
        Get report metadata, including report type and extended metadata.
        Results are cached to avoid redundant API calls.
        
        Args:
            report_id (str): The ID of the Salesforce report
            
        Returns:
            dict: Complete report metadata
        """
        url = f"{self.instance_url}{self.base_api_path}/{report_id}/describe"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def execute_report(self, report_id: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Execute a report with optional metadata modifications.
        
        Args:
            report_id (str): The ID of the Salesforce report
            metadata (dict, optional): Modified metadata to use for the report
            
        Returns:
            dict: Report execution results
        """
        url = f"{self.instance_url}{self.base_api_path}/{report_id}"
        
        if metadata:
            response = requests.post(url, headers=self.headers, json={'reportMetadata': metadata})
        else:
            response = requests.get(url, headers=self.headers)
            
        response.raise_for_status()
        return response.json()

    def fetch_all_report_data(self, report_id: str, id_column: str) -> Tuple[List[str], List[List]]:
        """
        Fetches all data from a report by paginating using a column value as a filter.
        
        Args:
            report_id (str): The ID of the Salesforce report
            id_column (str): The column name to use for pagination (should be ordered, like ID or date)
            
        Returns:
            tuple: (list of column names, list of rows where each row is a list of values)
        """
        def update_metadata(base_metadata: Dict, last_seen_value: str) -> Dict:
            metadata = base_metadata.copy()
            
            new_filter = {
                "column": id_column,
                "operator": "greaterThan",
                "value": last_seen_value
            }
            
            # Check if we need to add the filter or update existing one
            filter_exists = False
            for f in metadata.get('reportFilters', []):
                if f['column'] == id_column:
                    f.update(new_filter)
                    filter_exists = True
                    break
                    
            if not filter_exists:
                if 'reportFilters' not in metadata:
                    metadata['reportFilters'] = []
                metadata['reportFilters'].append(new_filter)
                
                # Update the boolean filter if it exists
                if 'reportBooleanFilter' in metadata:
                    current_filter = metadata['reportBooleanFilter']
                    filter_number = len(metadata['reportFilters'])
                    metadata['reportBooleanFilter'] = f"({current_filter}) AND {filter_number}"
                else:
                    metadata['reportBooleanFilter'] = str(len(metadata['reportFilters']))
                    
            return metadata

        # Get initial report
        initial_response = self.execute_report(report_id)
        metadata = initial_response['reportMetadata']
        
        # Get column names
        columns = [detail['label'] for detail in metadata['detailColumns']]
        
        # Store all rows
        all_rows = []
        id_column_index = columns.index(id_column)
        
        while True:
            response = self.execute_report(report_id, metadata)
            
            # Extract the factMap data
            fact_map = response['factMap']
            if not fact_map:
                break
                
            # Process rows
            for key in fact_map:
                data_rows = fact_map[key]['dataRows']
                for data_row in data_rows:
                    row = [cell['label'] for cell in data_row['dataCells']]
                    all_rows.append(row)
            
            if not all_rows:
                break
            
            # Update metadata with new filter value
            last_value = all_rows[-1][id_column_index]
            metadata = update_metadata(metadata, last_value)
            
            # Check if we've got all data
            if response.get('allData', False):
                break
        
        return columns, all_rows


# Example usage:
"""
# Initialize with specific API version
fetcher = SalesforceReportFetcher(
    access_token="your_access_token",
    instance_url="https://your-instance.salesforce.com",
    api_version="57.0"  # or whatever version you need
)

# Rest of the usage remains the same
report_id = "00OxxxxxxxxxxxxxxxxX"
id_column = "Id"
columns, rows = fetcher.fetch_all_report_data(report_id, id_column)
"""