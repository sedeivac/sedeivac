# Data Quality Analysis Tool

A comprehensive Python tool for analyzing data quality with actionable recommendations and scoring.

## Overview

The `analyzeDataQuality.py` tool performs comprehensive data quality assessment for CSV files and database tables, providing:

- **Structure Identification**: Column types, max lengths, and possible primary keys
- **Quality Metrics**: Null percentages, duplicates, distributions, and outliers
- **Format Validation**: Email, date, and text format checking
- **Quality Scoring**: 1-5 scale scoring per column and overall
- **Actionable Recommendations**: Concrete SQL examples and prioritized action plans
- **Executive Summary**: Clear visualization with ✅ ⚠️ ❌ indicators

## Quick Start

### Prerequisites
- Python 3.7 or higher (no external dependencies required)

### Basic Usage

```bash
# Make the script executable
chmod +x analyzeDataQuality.py

# Analyze a CSV file
python3 analyzeDataQuality.py sample_data.csv

# Export detailed report to JSON
python3 analyzeDataQuality.py sample_data.csv --export report.json
```

## Features

### 1. Structure Identification
- Automatically infers data types (INT, VARCHAR, DATE, DECIMAL, BOOLEAN, EMAIL, TEXT)
- Calculates maximum field lengths
- Identifies possible primary keys

### 2. Data Quality Evaluation
For each column:
- **Null Analysis**: Percentage of null/empty values
- **Duplicate Analysis**: Unique value counts and duplicate percentages
- **Distribution Analysis**:
  - Numeric: min, max, mean, median, standard deviation
  - Categorical: top categories and counts
  - Dates: date ranges and spans
- **Outlier Detection**: IQR method for numeric fields
- **Format Validation**:
  - Email format validation
  - Date format consistency
  - Special character detection

### 3. Quality Rules Recommendations
- NOT NULL constraints for columns with low null rates
- Range checks for numeric values
- Domain constraints for categorical columns
- Format validation rules
- Concrete SQL implementation examples

### 4. Executive Summary
- Quality score (1-5) per column
- Overall table quality score
- Main risks and issues identified
- Specific improvement recommendations

### 5. Prioritized Action Plan
- **🔴 Critical**: Immediate fixes required
- **🟠 High Priority**: 1-2 week timeline
- **🟡 Medium Priority**: 1 month timeline
- **🟢 Low Priority**: Continuous improvement
- **Quality KPIs**: Metrics to monitor over time
- **Implementation Roadmap**: Step-by-step timeline

## Example Output

```
================================================================================
DATA QUALITY ANALYSIS REPORT
================================================================================

Data Source: sample_data.csv
Total Records: 100
Total Columns: 6

✅ Overall Quality Score: 4.83/5.0

📊 Column Scores:
   ✅ customer_id: 5.0/5.0
   ✅ email: 4.5/5.0
   ✅ age: 5.0/5.0
   ✅ signup_date: 4.5/5.0
   ✅ status: 5.0/5.0
   ✅ total_purchases: 5.0/5.0

🔴 CRITICAL PRIORITY:
   ❌ Fix invalid EMAIL formats in 'email'
   ❌ Fix invalid DATE formats in 'signup_date'
```

## Command Line Options

```
usage: analyzeDataQuality.py [-h] [--export FILE] data_source

positional arguments:
  data_source      Path to CSV file or database table name

optional arguments:
  -h, --help       Show help message
  --export FILE    Export detailed report to JSON file
```

## Documentation

- **[USAGE.md](USAGE.md)**: Comprehensive usage guide with examples
- **[requirements.txt](requirements.txt)**: Python dependencies (standard library only)
- **[sample_data.csv](sample_data.csv)**: Sample dataset for testing

## Sample Data

A sample customer dataset is included (`sample_data.csv`) with:
- 100 customer records
- 6 columns (customer_id, email, age, signup_date, status, total_purchases)
- Intentional data quality issues for demonstration

## Quality Score Calculation

Scores range from 1.0 to 5.0:
- **5.0**: Excellent - No issues detected
- **4.0-4.9**: Good - Minor issues
- **3.0-3.9**: Fair - Some issues need attention
- **2.0-2.9**: Poor - Multiple issues
- **1.0-1.9**: Critical - Severe quality problems

Points deducted for:
- Null values: -0.5 to -2.0 based on percentage
- Format issues: -0.5 per issue type
- Outliers: -0.3 if detected

## Supported Data Types

- **INT**: Integer numbers
- **DECIMAL**: Floating-point numbers
- **VARCHAR**: Short text (≤255 chars average)
- **TEXT**: Long text (>255 chars average)
- **DATE**: Various date formats
- **BOOLEAN**: True/false values
- **EMAIL**: Email addresses

## Visual Indicators

- ✅ Green: Good quality (score ≥ 4.0 or < 5% nulls)
- ⚠️ Yellow: Needs attention (score ≥ 3.0 or 5-20% nulls)
- ❌ Red: Critical issue (score < 3.0 or > 20% nulls)

## Advanced Usage

### Batch Processing
```bash
# Analyze all CSV files in a directory
for file in *.csv; do
    python3 analyzeDataQuality.py "$file" --export "${file%.csv}_quality.json"
done
```

### Integration Example
```bash
# In CI/CD pipeline
python3 analyzeDataQuality.py data.csv --export quality_report.json
# Parse JSON and fail build if quality score < 4.0
```

## Contributing

To extend functionality:
1. Add new data type detection in `_infer_type()`
2. Add format validators (phone numbers, SSN, etc.)
3. Add new quality metrics
4. Enhance recommendation engine
5. Add database connectivity

## License

This tool is provided as-is for data quality assessment purposes.

---

## About

Created as part of a comprehensive data engineering toolkit for data quality management and governance.
