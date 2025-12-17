# Data Quality Analysis Tool - Examples

This directory contains example datasets and use cases for the data quality analysis tool.

## Example 1: Customer Data Analysis

The main `sample_data.csv` in the root directory demonstrates a customer dataset with common data quality issues:
- Invalid email formats
- Inconsistent date formats
- Missing values
- Outliers in numeric fields

### Running the Analysis

```bash
python3 ../analyzeDataQuality.py ../sample_data.csv
```

### Expected Results
- Overall Quality Score: ~4.8/5.0
- Issues detected: Invalid emails, inconsistent date formats
- Recommendations: Format standardization, validation rules

## Example 2: Batch Processing Multiple Files

Process all CSV files in a directory:

```bash
#!/bin/bash
# analyze_all.sh

for file in *.csv; do
    echo "Analyzing $file..."
    python3 ../analyzeDataQuality.py "$file" --export "${file%.csv}_quality.json"
    echo "---"
done
```

Make it executable and run:
```bash
chmod +x analyze_all.sh
./analyze_all.sh
```

## Example 3: Quality Threshold Checking

Check if data meets quality standards:

```bash
#!/bin/bash
# check_quality.sh

FILE=$1
THRESHOLD=4.0

python3 ../analyzeDataQuality.py "$FILE" --export temp_report.json

# Extract overall score from JSON (requires jq)
if command -v jq &> /dev/null; then
    SCORE=$(jq -r '.overall_score' temp_report.json)
    
    if (( $(echo "$SCORE < $THRESHOLD" | bc -l) )); then
        echo "❌ Quality check FAILED: Score $SCORE is below threshold $THRESHOLD"
        exit 1
    else
        echo "✅ Quality check PASSED: Score $SCORE meets threshold $THRESHOLD"
        exit 0
    fi
else
    echo "⚠️  jq not installed, cannot parse score automatically"
fi
```

## Example 4: Creating Test Data

Generate test data with quality issues:

```python
#!/usr/bin/env python3
# generate_test_data.py

import csv
import random
from datetime import datetime, timedelta

def generate_test_data(filename, num_rows=1000):
    """Generate test data with intentional quality issues."""
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'email', 'age', 'date', 'amount'])
        
        for i in range(1, num_rows + 1):
            # Intentionally add quality issues
            
            # 5% null emails
            if random.random() < 0.05:
                email = ''
            # 2% invalid emails
            elif random.random() < 0.02:
                email = f'invalid.email{i}'
            else:
                email = f'user{i}@example.com'
            
            # Random ages with some outliers
            if random.random() < 0.01:
                age = random.randint(1, 150)  # Outlier
            else:
                age = random.randint(18, 75)
            
            # Dates with inconsistent formats
            base_date = datetime(2023, 1, 1)
            date_offset = random.randint(0, 365)
            date = base_date + timedelta(days=date_offset)
            
            # 10% use different format
            if random.random() < 0.1:
                date_str = date.strftime('%m/%d/%Y')
            else:
                date_str = date.strftime('%Y-%m-%d')
            
            # Amount with some nulls
            if random.random() < 0.03:
                amount = ''
            else:
                amount = round(random.uniform(10, 10000), 2)
            
            writer.writerow([
                i,
                f'User{i}',
                email,
                age,
                date_str,
                amount
            ])
    
    print(f"Generated {filename} with {num_rows} rows")

if __name__ == '__main__':
    generate_test_data('test_data_1000.csv', 1000)
```

## Example 5: Automated Quality Reporting

Create a weekly quality report:

```bash
#!/bin/bash
# weekly_quality_report.sh

REPORT_DIR="quality_reports"
DATE=$(date +%Y%m%d)

mkdir -p "$REPORT_DIR"

echo "=== Data Quality Report - $(date) ===" > "$REPORT_DIR/summary_$DATE.txt"

for file in data/*.csv; do
    basename=$(basename "$file" .csv)
    echo "Processing $basename..." | tee -a "$REPORT_DIR/summary_$DATE.txt"
    
    python3 analyzeDataQuality.py "$file" --export "$REPORT_DIR/${basename}_$DATE.json"
    
    # Extract key metrics (requires jq)
    if command -v jq &> /dev/null; then
        score=$(jq -r '.overall_score' "$REPORT_DIR/${basename}_$DATE.json")
        echo "  Score: $score/5.0" | tee -a "$REPORT_DIR/summary_$DATE.txt"
    fi
    echo "" | tee -a "$REPORT_DIR/summary_$DATE.txt"
done

echo "Report saved to $REPORT_DIR/summary_$DATE.txt"
```

## Example 6: CI/CD Integration

GitHub Actions workflow example:

```yaml
# .github/workflows/data-quality.yml
name: Data Quality Check

on:
  push:
    paths:
      - 'data/*.csv'
  pull_request:
    paths:
      - 'data/*.csv'

jobs:
  quality-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Run Data Quality Analysis
      run: |
        for file in data/*.csv; do
          python3 analyzeDataQuality.py "$file" --export "${file%.csv}_quality.json"
        done
    
    - name: Check Quality Threshold
      run: |
        # Add quality threshold validation
        # Fail if any dataset scores below 4.0
        python3 scripts/check_quality_threshold.py --threshold 4.0
    
    - name: Upload Quality Reports
      uses: actions/upload-artifact@v2
      with:
        name: quality-reports
        path: '**/*_quality.json'
```

## Common Use Cases

### Use Case 1: Pre-Production Data Validation
Before deploying data to production, run quality analysis to ensure:
- No critical format issues
- Acceptable null percentages
- No unexpected outliers
- Overall quality score > 4.0

### Use Case 2: Data Migration Validation
After migrating data:
1. Analyze source data
2. Analyze target data
3. Compare quality scores
4. Validate no degradation occurred

### Use Case 3: Regular Data Health Monitoring
Set up weekly/monthly automated analysis:
- Track quality trends over time
- Alert on quality degradation
- Monitor KPIs
- Generate executive reports

### Use Case 4: Data Onboarding
When receiving new data:
1. Run initial quality analysis
2. Identify major issues
3. Work with data provider on fixes
4. Re-analyze after corrections
5. Accept only when quality > threshold

## Tips and Best Practices

1. **Start with sample data**: Analyze a small sample first to understand the dataset
2. **Set quality thresholds**: Define minimum acceptable scores for your use case
3. **Automate regular checks**: Don't wait for issues to be discovered in production
4. **Track trends**: Compare reports over time to see improvements or degradation
5. **Document exceptions**: Some low-quality data may be acceptable with proper documentation
6. **Prioritize fixes**: Start with critical issues, then work down the priority list

## Troubleshooting

### Large Files
For files > 100MB, consider:
```bash
# Analyze first 10,000 rows
head -n 10001 large_file.csv > sample.csv
python3 analyzeDataQuality.py sample.csv
```

### Memory Issues
If you encounter memory errors:
```python
# Modify the script to use chunking
# Process data in batches of 10,000 rows
```

### Encoding Issues
```bash
# Convert to UTF-8 first
iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv
python3 analyzeDataQuality.py output.csv
```

## Additional Resources

- Main documentation: [../USAGE.md](../USAGE.md)
- Sample data: [../sample_data.csv](../sample_data.csv)
- Tool source: [../analyzeDataQuality.py](../analyzeDataQuality.py)
