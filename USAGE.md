# Data Quality Analysis Tool - Usage Guide

## Overview

The `analyzeDataQuality.py` tool performs comprehensive data quality assessment with actionable recommendations and scoring for CSV files and database tables.

## Features

### 1. Structure Identification
- Column names and inferred data types (INT, VARCHAR, DATE, DECIMAL, BOOLEAN, EMAIL, TEXT)
- Maximum observed length for text fields
- Automatic detection of possible primary keys or natural keys

### 2. Detailed Data Quality Evaluation
For each column, the tool analyzes:
- **Null/Empty Analysis**: Percentage of null or empty values
- **Duplicate Analysis**: Percentage of duplicate values and unique value count
- **Distribution Analysis**:
  - Numeric fields: min, max, mean, median, standard deviation
  - Categorical fields: count of main categories
  - Date fields: date range and span
- **Outlier Detection**: Uses IQR (Interquartile Range) method for numeric fields
- **Format Validation**:
  - Date format consistency
  - Email validation
  - Special character detection
  - Phone number patterns
  - Other domain-specific validations

### 3. Data Quality Rules Recommendations
Automatically proposes:
- NOT NULL constraints for columns with low null percentages
- Range checks for numeric values
- Domain constraints for categorical columns
- Format validation rules
- Includes concrete SQL examples for implementation

### 4. Executive Summary
Provides:
- Quality score (1-5) per column
- Overall table quality score
- Main risks and problems detected
- Specific recommendations categorized by type

### 5. Prioritized Action Plan
- **Critical Priority**: Issues requiring immediate action
- **High Priority**: Important improvements (1-2 weeks)
- **Medium Priority**: Enhancements (1 month)
- **Low Priority**: Continuous improvement items
- **Quality KPIs**: Metrics to monitor over time
- **Implementation Roadmap**: Timeline for improvements

## Installation

No installation required! The tool uses only Python standard library.

### Requirements
- Python 3.7 or higher

### Verify Python Version
```bash
python3 --version
```

## Usage

### Basic Usage

Analyze a CSV file:
```bash
python3 analyzeDataQuality.py data.csv
```

### Export Report to JSON

```bash
python3 analyzeDataQuality.py data.csv --export report.json
```

### Make the Script Executable

```bash
chmod +x analyzeDataQuality.py
./analyzeDataQuality.py data.csv
```

## Command Line Options

```
usage: analyzeDataQuality.py [-h] [--export FILE] data_source

positional arguments:
  data_source      Path to CSV file or database table name

optional arguments:
  -h, --help       show this help message and exit
  --export FILE    Export detailed report to JSON file
```

## Examples

### Example 1: Basic Analysis

```bash
python3 analyzeDataQuality.py customer_data.csv
```

Output includes:
- Complete structure analysis
- Quality metrics for each column
- Visual indicators (✅ ⚠️ ❌)
- Actionable recommendations
- Prioritized action plan

### Example 2: Export to JSON

```bash
python3 analyzeDataQuality.py sales_data.csv --export sales_quality_report.json
```

Creates a detailed JSON report with:
- All metrics and scores
- Structure information
- Quality assessments
- Timestamp of analysis

### Example 3: Analyze and Review

```bash
# Run analysis
python3 analyzeDataQuality.py employee_data.csv

# Export for sharing
python3 analyzeDataQuality.py employee_data.csv --export employee_quality.json
```

## Understanding the Output

### Visual Indicators

- ✅ **Green checkmark**: Good quality (score ≥ 4.0, or < 5% nulls)
- ⚠️ **Yellow warning**: Needs attention (score ≥ 3.0, or 5-20% nulls)
- ❌ **Red cross**: Critical issue (score < 3.0, or > 20% nulls)

### Quality Scores

Scores range from 1.0 to 5.0:
- **5.0**: Excellent - No issues detected
- **4.0-4.9**: Good - Minor issues
- **3.0-3.9**: Fair - Some issues need attention
- **2.0-2.9**: Poor - Multiple issues
- **1.0-1.9**: Critical - Severe quality problems

### Score Calculation

Points are deducted for:
- Null values: -0.5 to -2.0 based on percentage
- Format issues: -0.5 per issue type (max 2 issues)
- Outliers: -0.3 if detected

## Sample Output

```
================================================================================
DATA QUALITY ANALYSIS REPORT
================================================================================

Data Source: customer_data.csv
Total Records: 1000
Total Columns: 5

================================================================================
1. STRUCTURE IDENTIFICATION
================================================================================

Column Name                    Type            Max Length  
--------------------------------------------------------------------------------
customer_id                    INT             N/A         
email                          EMAIL           N/A         
age                            INT             N/A         
signup_date                    DATE            N/A         
status                         VARCHAR         8           

📌 Possible Primary Keys:
  ✓ customer_id

================================================================================
2. DETAILED DATA QUALITY EVALUATION
================================================================================

📊 Column: customer_id
--------------------------------------------------------------------------------
✅ Null/Empty: 0.00%
✅ Duplicates: 0.00% (1000 unique values)

📈 Distribution:
   Min: 1.00, Max: 1000.00
   Mean: 500.50, Median: 500.50
   StdDev: 288.82

✅ Quality Score: 5.0/5.0

📊 Column: email
--------------------------------------------------------------------------------
⚠️ Null/Empty: 8.50%
✅ Duplicates: 2.19% (892 unique values)

❌ Format Issues:
   - {'issue': 'Invalid email formats', 'count': 5, 'examples': ['user@', 'invalid.email', ...]}

⚠️ Quality Score: 3.7/5.0

[... more columns ...]

================================================================================
3. PROPOSED DATA QUALITY AND BUSINESS RULES
================================================================================

📋 Recommended Rules:

1. customer_id should not allow null values
   Type: NOT NULL
   SQL: ALTER TABLE table_name MODIFY customer_id INT NOT NULL;

2. customer_id should be between 1.00 and 1000.00
   Type: RANGE CHECK
   SQL: ALTER TABLE table_name ADD CONSTRAINT chk_customer_id CHECK (customer_id BETWEEN 1.00 AND 1000.00);

[... more rules ...]

================================================================================
4. EXECUTIVE SUMMARY
================================================================================

✅ Overall Quality Score: 4.2/5.0

📊 Column Scores:
   ⚠️ email: 3.7/5.0
   ✅ age: 4.5/5.0
   ✅ customer_id: 5.0/5.0
   ✅ signup_date: 4.8/5.0
   ✅ status: 4.3/5.0

⚠️ Main Issues:
   • Format inconsistencies in: email

💡 Recommendations:
   • Standardize format for 'email' - implement validation at data entry point
   • Investigate and handle missing values in 'email' (consider imputation, default values, or making it optional)

================================================================================
5. ACTION PLAN
================================================================================

🔴 CRITICAL PRIORITY (Immediate Action Required):
   ✅ No critical issues

🟠 HIGH PRIORITY (1-2 Weeks):
   ⚠️ Reduce missing values in 'email' (currently 8.5%)

🟡 MEDIUM PRIORITY (1 Month):
   • Standardize text format in 'email'

🟢 LOW PRIORITY (Continuous Improvement):
   • Enhance data quality for 'email' (score: 3.7/5)

📊 Quality KPIs to Monitor:
   • Track null percentage per column (target: <5%)
   • Monitor duplicate rates in key columns (target: <10%)
   • Measure format compliance (target: 100%)
   • Track overall quality score (target: >4.0)
   • Monitor outlier detection rate (review threshold quarterly)

🗓️ Implementation Roadmap:
   • Week 1-2: Address all critical priority items
   • Week 3-4: Implement high priority fixes and validations
   • Month 2: Standardize formats and complete medium priority items
   • Month 3: Enhance data quality and implement low priority improvements
   • Ongoing: Monitor KPIs and maintain data quality standards

================================================================================
ANALYSIS COMPLETE
================================================================================
```

## Supported Data Types

The tool automatically detects and analyzes:

1. **INT**: Integer numbers
2. **DECIMAL**: Floating-point numbers
3. **VARCHAR**: Short text fields (≤255 chars average)
4. **TEXT**: Long text fields (>255 chars average)
5. **DATE**: Date values in various formats
6. **BOOLEAN**: True/false values
7. **EMAIL**: Email addresses

## Format Validation

Automatically validates:

- **Dates**: YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY, YYYY/MM/DD
- **Emails**: RFC-compliant email format
- **Text**: Unusual special characters
- **Numbers**: Consistency and outliers

## Best Practices

1. **Review Before Action**: Always review the recommendations before implementing changes
2. **Test Changes**: Test SQL changes on a copy of data first
3. **Incremental Fixes**: Address critical issues first, then move to lower priorities
4. **Monitor KPIs**: Track quality metrics over time
5. **Regular Analysis**: Run analysis periodically (weekly/monthly) to track improvements

## Troubleshooting

### CSV Encoding Issues

If you encounter encoding errors:
```bash
# Convert CSV to UTF-8
iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv
python3 analyzeDataQuality.py output.csv
```

### Large Files

For very large CSV files (>100MB), consider:
1. Using database import and sampling
2. Splitting the file into chunks
3. Analyzing a representative sample first

### Permission Issues

If you get permission errors:
```bash
chmod +x analyzeDataQuality.py
```

## Advanced Usage

### Scripting and Automation

```bash
#!/bin/bash
# Analyze all CSV files in a directory

for file in *.csv; do
    echo "Analyzing $file..."
    python3 analyzeDataQuality.py "$file" --export "${file%.csv}_quality.json"
done
```

### Integration with CI/CD

```bash
# In your pipeline
python3 analyzeDataQuality.py data.csv --export quality_report.json

# Check if quality score meets threshold
# Parse JSON and fail build if score < 4.0
```

## Contributing

To extend the tool:

1. Add new data type detection in `_infer_type()`
2. Add new format validators (e.g., phone numbers, SSN)
3. Add new quality metrics
4. Enhance recommendation engine
5. Add database connectivity

## License

This tool is provided as-is for data quality assessment purposes.
