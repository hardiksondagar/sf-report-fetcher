# sf-report-fetcher

A Python utility to fetch complete Salesforce reports, bypassing the 2000-row limit using smart pagination.

## The Problem

Salesforce's Report API has a limitation where it won't return more than 2000 rows per request. While there are various workarounds suggested online (like using multiple reports or offset-based pagination), none of them work reliably for large reports.

## The Solution

This package implements a smart pagination strategy using column-based filtering. Instead of using offset pagination (which Salesforce doesn't support), it:

1. Fetches the first batch of data
2. Uses the last value of a specified column as a filter
3. Fetches the next batch where the column value is greater than the last seen value
4. Repeats until all data is retrieved

## Installation

```bash
pip install sf-report-fetcher
```

## Basic Usage

```python
from salesforce_report_fetcher import SalesforceReportFetcher

# Initialize the fetcher
fetcher = SalesforceReportFetcher(
    access_token="your_salesforce_access_token",
    instance_url="https://your-instance.salesforce.com"
)

# Fetch all data from a report
report_id = "00OxxxxxxxxxxxxxxxxX"  # Your Salesforce report ID
id_column = "Id"  # Any ordered column in your report (usually Id or CreatedDate)

# Get the data
columns, rows = fetcher.fetch_all_report_data(report_id, id_column)

# Work with the data
print(f"Retrieved {len(rows)} rows")
for row in rows:
    for col_name, value in zip(columns, row):
        print(f"{col_name}: {value}")
```

## Advanced Usage

### Specifying Salesforce API Version

You can specify which Salesforce API version to use:

```python
# Use specific API version
fetcher = SalesforceReportFetcher(
    access_token="your_token",
    instance_url="https://instance.salesforce.com",
    api_version="47.0"  # Specify your desired API version
)
```

### Getting Report Metadata

```python
# Get report metadata (cached)
metadata = fetcher.get_metadata(report_id)
print("Available fields:", [field['label'] for field in metadata['reportType']['fields']])
```

### Executing Reports with Custom Metadata

```python
# Execute report with custom metadata
custom_metadata = {
    "reportFilters": [
        {
            "column": "CreatedDate",
            "operator": "greaterThan",
            "value": "2024-01-01"
        }
    ]
}
results = fetcher.execute_report(report_id, custom_metadata)
```

## Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `access_token` | Your Salesforce access token | Required |
| `instance_url` | Your Salesforce instance URL | Required |
| `api_version` | Salesforce API version to use | "57.0" |

## Requirements

- Python 3.7+
- requests

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this in your projects!