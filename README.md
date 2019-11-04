# experimentsheets
Interface to log an experiment's results to google sheets

# Installation
The main dependency is pygsheets. Follow their setup instructions first.

# Usage
The provided class is used to authenticate to a sheet, claim a row within that sheet given a unique experiment id, and (possibly repeatedly) updating that row's results.

# Example
```python
def main():
    print("Instantiating")
    res = GSheetsResults("experimentsheets_example")
    unique_id = "experiment_{:08d}".format(int(random.random() * 1e6))
    print("Claiming row")
    res.claim_row(unique_id)
    experiment_result = ["data", 1, 2, 3.5, "gitid?", "foo"]
    print("Updating claimed row's data")
    res.update_claimed_row(experiment_result)
```
