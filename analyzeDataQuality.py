#!/usr/bin/env python3
"""
Data Quality Analysis Tool
Performs comprehensive data quality assessment with actionable recommendations and scoring
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import statistics
import math


class DataQualityAnalyzer:
    """Comprehensive data quality analyzer for CSV files and database tables."""
    
    def __init__(self, data_source: str):
        """
        Initialize the analyzer with a data source.
        
        Args:
            data_source: Path to CSV file or database table name
        """
        self.data_source = data_source
        self.data: List[Dict[str, Any]] = []
        self.columns: List[str] = []
        self.column_types: Dict[str, str] = {}
        self.column_max_lengths: Dict[str, int] = {}
        self.quality_metrics: Dict[str, Dict[str, Any]] = {}
        self.quality_scores: Dict[str, float] = {}
        self.overall_score: float = 0.0
        
    def load_data(self) -> bool:
        """Load data from the source."""
        if os.path.isfile(self.data_source) and self.data_source.endswith('.csv'):
            return self._load_csv()
        else:
            print(f"❌ Error: Unsupported data source: {self.data_source}")
            print(f"   Currently only CSV files are supported.")
            return False
    
    def _load_csv(self) -> bool:
        """Load data from CSV file."""
        try:
            with open(self.data_source, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.columns = reader.fieldnames or []
                self.data = list(reader)
            
            if not self.data:
                print(f"⚠️ Warning: CSV file is empty")
                return False
                
            print(f"✅ Loaded {len(self.data)} rows from {self.data_source}")
            return True
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return False
    
    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive data quality analysis."""
        print("\n" + "="*80)
        print("DATA QUALITY ANALYSIS REPORT")
        print("="*80)
        print(f"\nData Source: {self.data_source}")
        print(f"Total Records: {len(self.data)}")
        print(f"Total Columns: {len(self.columns)}")
        
        # 1. Structure Identification
        self._identify_structure()
        
        # 2. Detailed Data Quality Evaluation
        self._evaluate_quality()
        
        # 3. Proposed Data Quality Rules
        rules = self._propose_rules()
        
        # 4. Executive Summary
        summary = self._generate_summary()
        
        # 5. Action Plan
        action_plan = self._create_action_plan()
        
        return {
            'structure': self._get_structure_info(),
            'quality_metrics': self.quality_metrics,
            'quality_scores': self.quality_scores,
            'overall_score': self.overall_score,
            'proposed_rules': rules,
            'summary': summary,
            'action_plan': action_plan
        }
    
    def _identify_structure(self):
        """Identify and document data structure."""
        print("\n" + "="*80)
        print("1. STRUCTURE IDENTIFICATION")
        print("="*80)
        
        for col in self.columns:
            # Infer data type
            values = [row.get(col, '') for row in self.data]
            self.column_types[col] = self._infer_type(values)
            
            # Calculate max length for text fields
            if self.column_types[col] in ['VARCHAR', 'TEXT']:
                max_len = max((len(str(v)) for v in values if v), default=0)
                self.column_max_lengths[col] = max_len
        
        # Display structure
        print(f"\n{'Column Name':<30} {'Type':<15} {'Max Length':<12}")
        print("-" * 80)
        for col in self.columns:
            col_type = self.column_types[col]
            max_len = self.column_max_lengths.get(col, 'N/A')
            print(f"{col:<30} {col_type:<15} {str(max_len):<12}")
        
        # Identify possible keys
        possible_keys = self._identify_keys()
        print("\n📌 Possible Primary Keys:")
        if possible_keys:
            for key in possible_keys:
                print(f"  ✓ {key}")
        else:
            print("  ⚠️  No unique key columns found")
    
    def _infer_type(self, values: List[Any]) -> str:
        """Infer data type from values."""
        non_empty = [v for v in values if v and str(v).strip()]
        if not non_empty:
            return 'VARCHAR'
        
        # Sample values for type inference
        sample = non_empty[:min(100, len(non_empty))]
        
        # Check for boolean
        bool_values = {'true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n'}
        if all(str(v).lower() in bool_values for v in sample):
            return 'BOOLEAN'
        
        # Check for integer
        int_count = sum(1 for v in sample if self._is_integer(v))
        if int_count / len(sample) > 0.95:
            return 'INT'
        
        # Check for decimal
        float_count = sum(1 for v in sample if self._is_float(v))
        if float_count / len(sample) > 0.95:
            return 'DECIMAL'
        
        # Check for date
        date_count = sum(1 for v in sample if self._is_date(v))
        if date_count / len(sample) > 0.95:
            return 'DATE'
        
        # Check for email
        email_count = sum(1 for v in sample if self._is_email(v))
        if email_count / len(sample) > 0.95:
            return 'EMAIL'
        
        # Default to VARCHAR or TEXT
        avg_len = sum(len(str(v)) for v in sample) / len(sample)
        return 'TEXT' if avg_len > 255 else 'VARCHAR'
    
    def _is_integer(self, value: Any) -> bool:
        """Check if value is an integer."""
        try:
            int(str(value).replace(',', ''))
            return '.' not in str(value)
        except (ValueError, AttributeError):
            return False
    
    def _is_float(self, value: Any) -> bool:
        """Check if value is a float."""
        try:
            float(str(value).replace(',', ''))
            return True
        except (ValueError, AttributeError):
            return False
    
    def _is_date(self, value: Any) -> bool:
        """Check if value is a date."""
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
            r'^\d{2}-\d{2}-\d{4}$',  # DD-MM-YYYY
            r'^\d{4}/\d{2}/\d{2}$',  # YYYY/MM/DD
        ]
        return any(re.match(pattern, str(value)) for pattern in date_patterns)
    
    def _is_email(self, value: Any) -> bool:
        """Check if value is an email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(value)))
    
    def _identify_keys(self) -> List[str]:
        """Identify possible primary key columns."""
        possible_keys = []
        total_rows = len(self.data)
        
        for col in self.columns:
            values = [row.get(col, '') for row in self.data]
            non_empty = [v for v in values if v and str(v).strip()]
            unique_values = set(non_empty)
            
            # A column is a possible key if it has unique non-null values
            if len(unique_values) == total_rows and len(non_empty) == total_rows:
                possible_keys.append(col)
        
        return possible_keys
    
    def _evaluate_quality(self):
        """Evaluate data quality for each column."""
        print("\n" + "="*80)
        print("2. DETAILED DATA QUALITY EVALUATION")
        print("="*80)
        
        for col in self.columns:
            print(f"\n📊 Column: {col}")
            print("-" * 80)
            
            metrics = self._analyze_column(col)
            self.quality_metrics[col] = metrics
            
            # Calculate quality score for this column
            score = self._calculate_column_score(metrics)
            self.quality_scores[col] = score
            
            # Display metrics
            self._display_column_metrics(col, metrics, score)
    
    def _analyze_column(self, col: str) -> Dict[str, Any]:
        """Analyze a single column."""
        values = [row.get(col, '') for row in self.data]
        total = len(values)
        
        metrics = {
            'total_values': total,
            'null_count': 0,
            'empty_count': 0,
            'null_percentage': 0.0,
            'unique_count': 0,
            'duplicate_percentage': 0.0,
            'distribution': {},
            'outliers': [],
            'format_issues': []
        }
        
        # Count nulls and empties
        non_empty_values = []
        for v in values:
            if v is None or str(v).strip() == '':
                if v is None:
                    metrics['null_count'] += 1
                else:
                    metrics['empty_count'] += 1
            else:
                non_empty_values.append(str(v))
        
        total_null_empty = metrics['null_count'] + metrics['empty_count']
        metrics['null_percentage'] = (total_null_empty / total * 100) if total > 0 else 0
        
        # Count unique values
        unique_values = set(non_empty_values)
        metrics['unique_count'] = len(unique_values)
        
        # Calculate duplicate percentage
        if non_empty_values:
            metrics['duplicate_percentage'] = ((len(non_empty_values) - len(unique_values)) / len(non_empty_values) * 100)
        
        # Distribution analysis based on type
        col_type = self.column_types[col]
        
        if col_type in ['INT', 'DECIMAL']:
            metrics['distribution'] = self._analyze_numeric_distribution(non_empty_values)
            metrics['outliers'] = self._detect_numeric_outliers(non_empty_values)
        elif col_type == 'DATE':
            metrics['distribution'] = self._analyze_date_distribution(non_empty_values)
            metrics['format_issues'] = self._detect_date_format_issues(non_empty_values)
        elif col_type == 'EMAIL':
            metrics['format_issues'] = self._detect_email_issues(non_empty_values)
        else:
            metrics['distribution'] = self._analyze_categorical_distribution(non_empty_values)
        
        # Generic format validation
        if col_type == 'VARCHAR' or col_type == 'TEXT':
            metrics['format_issues'].extend(self._detect_text_issues(non_empty_values))
        
        return metrics
    
    def _analyze_numeric_distribution(self, values: List[str]) -> Dict[str, Any]:
        """Analyze distribution of numeric values."""
        numeric_values = []
        for v in values:
            try:
                numeric_values.append(float(str(v).replace(',', '')))
            except ValueError:
                continue
        
        if not numeric_values:
            return {}
        
        return {
            'min': min(numeric_values),
            'max': max(numeric_values),
            'mean': statistics.mean(numeric_values),
            'median': statistics.median(numeric_values),
            'stdev': statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0,
            'count': len(numeric_values)
        }
    
    def _detect_numeric_outliers(self, values: List[str]) -> List[Any]:
        """Detect outliers in numeric data using IQR method."""
        numeric_values = []
        for v in values:
            try:
                numeric_values.append(float(str(v).replace(',', '')))
            except ValueError:
                continue
        
        if len(numeric_values) < 4:
            return []
        
        sorted_values = sorted(numeric_values)
        q1 = sorted_values[len(sorted_values) // 4]
        q3 = sorted_values[3 * len(sorted_values) // 4]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [v for v in numeric_values if v < lower_bound or v > upper_bound]
        return outliers[:10]  # Return first 10 outliers
    
    def _analyze_date_distribution(self, values: List[str]) -> Dict[str, Any]:
        """Analyze distribution of date values."""
        dates = []
        for v in values:
            parsed = self._parse_date(v)
            if parsed:
                dates.append(parsed)
        
        if not dates:
            return {}
        
        return {
            'min_date': min(dates).strftime('%Y-%m-%d'),
            'max_date': max(dates).strftime('%Y-%m-%d'),
            'count': len(dates),
            'range_days': (max(dates) - min(dates)).days
        }
    
    def _parse_date(self, value: str) -> Optional[datetime]:
        """Parse date from string."""
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y']
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None
    
    def _detect_date_format_issues(self, values: List[str]) -> List[Dict[str, str]]:
        """Detect inconsistent date formats."""
        format_counter = Counter()
        issues = []
        
        for v in values:
            detected_format = None
            if re.match(r'^\d{4}-\d{2}-\d{2}$', v):
                detected_format = 'YYYY-MM-DD'
            elif re.match(r'^\d{2}/\d{2}/\d{4}$', v):
                detected_format = 'MM/DD/YYYY'
            elif re.match(r'^\d{2}-\d{2}-\d{4}$', v):
                detected_format = 'DD-MM-YYYY'
            elif re.match(r'^\d{4}/\d{2}/\d{2}$', v):
                detected_format = 'YYYY/MM/DD'
            
            if detected_format:
                format_counter[detected_format] += 1
        
        if len(format_counter) > 1:
            issues.append({
                'issue': 'Inconsistent date formats',
                'details': f'Found formats: {dict(format_counter)}'
            })
        
        return issues
    
    def _detect_email_issues(self, values: List[str]) -> List[Dict[str, str]]:
        """Detect email format issues."""
        issues = []
        invalid_emails = []
        
        for v in values:
            if not self._is_email(v):
                invalid_emails.append(v)
        
        if invalid_emails:
            issues.append({
                'issue': 'Invalid email formats',
                'count': len(invalid_emails),
                'examples': invalid_emails[:5]
            })
        
        return issues
    
    def _detect_text_issues(self, values: List[str]) -> List[Dict[str, str]]:
        """Detect text format issues."""
        issues = []
        special_char_pattern = r'[^\w\s@.\-,/()]'
        
        special_char_values = [v for v in values if re.search(special_char_pattern, v)]
        
        if special_char_values and len(special_char_values) / len(values) < 0.1:
            issues.append({
                'issue': 'Unusual special characters',
                'count': len(special_char_values),
                'examples': special_char_values[:5]
            })
        
        return issues
    
    def _analyze_categorical_distribution(self, values: List[str]) -> Dict[str, Any]:
        """Analyze distribution of categorical values."""
        counter = Counter(values)
        top_categories = counter.most_common(10)
        
        return {
            'unique_categories': len(counter),
            'top_categories': dict(top_categories),
            'total_count': len(values)
        }
    
    def _calculate_column_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate quality score for a column (1-5 scale)."""
        score = 5.0
        
        # Deduct for null/empty values
        null_pct = metrics['null_percentage']
        if null_pct > 50:
            score -= 2.0
        elif null_pct > 20:
            score -= 1.0
        elif null_pct > 5:
            score -= 0.5
        
        # Deduct for format issues
        if metrics['format_issues']:
            score -= 0.5 * min(len(metrics['format_issues']), 2)
        
        # Deduct for outliers
        if metrics['outliers']:
            score -= 0.3
        
        return max(1.0, score)
    
    def _display_column_metrics(self, col: str, metrics: Dict[str, Any], score: float):
        """Display metrics for a column."""
        # Null/Empty percentage
        null_pct = metrics['null_percentage']
        null_indicator = '✅' if null_pct < 5 else '⚠️' if null_pct < 20 else '❌'
        print(f"{null_indicator} Null/Empty: {null_pct:.2f}%")
        
        # Duplicates
        dup_pct = metrics['duplicate_percentage']
        dup_indicator = '✅' if dup_pct < 20 else '⚠️' if dup_pct < 50 else '❌'
        print(f"{dup_indicator} Duplicates: {dup_pct:.2f}% ({metrics['unique_count']} unique values)")
        
        # Distribution
        if metrics['distribution']:
            print(f"\n📈 Distribution:")
            dist = metrics['distribution']
            if 'min' in dist:
                print(f"   Min: {dist['min']:.2f}, Max: {dist['max']:.2f}")
                print(f"   Mean: {dist['mean']:.2f}, Median: {dist['median']:.2f}")
                print(f"   StdDev: {dist['stdev']:.2f}")
            elif 'min_date' in dist:
                print(f"   Date Range: {dist['min_date']} to {dist['max_date']}")
                print(f"   Days Span: {dist['range_days']}")
            elif 'top_categories' in dist:
                print(f"   Unique Categories: {dist['unique_categories']}")
                print(f"   Top Values: {list(dist['top_categories'].items())[:5]}")
        
        # Outliers
        if metrics['outliers']:
            print(f"\n⚠️  Outliers Detected: {len(metrics['outliers'])} values")
            print(f"   Examples: {metrics['outliers'][:5]}")
        
        # Format Issues
        if metrics['format_issues']:
            print(f"\n❌ Format Issues:")
            for issue in metrics['format_issues']:
                print(f"   - {issue}")
        
        # Quality Score
        score_indicator = '✅' if score >= 4 else '⚠️' if score >= 3 else '❌'
        print(f"\n{score_indicator} Quality Score: {score:.1f}/5.0")
    
    def _propose_rules(self) -> List[Dict[str, str]]:
        """Propose data quality and business rules."""
        print("\n" + "="*80)
        print("3. PROPOSED DATA QUALITY AND BUSINESS RULES")
        print("="*80)
        
        rules = []
        
        for col in self.columns:
            metrics = self.quality_metrics[col]
            col_type = self.column_types[col]
            
            # Rule for nulls
            if metrics['null_percentage'] < 5:
                rules.append({
                    'column': col,
                    'rule_type': 'NOT NULL',
                    'description': f'{col} should not allow null values',
                    'sql': f'ALTER TABLE table_name MODIFY {col} {col_type} NOT NULL;'
                })
            
            # Rules for numeric ranges
            if col_type in ['INT', 'DECIMAL'] and metrics['distribution']:
                dist = metrics['distribution']
                rules.append({
                    'column': col,
                    'rule_type': 'RANGE CHECK',
                    'description': f'{col} should be between {dist["min"]:.2f} and {dist["max"]:.2f}',
                    'sql': f'ALTER TABLE table_name ADD CONSTRAINT chk_{col} CHECK ({col} BETWEEN {dist["min"]:.2f} AND {dist["max"]:.2f});'
                })
            
            # Rules for categorical columns with low cardinality
            if col_type == 'VARCHAR' and metrics['distribution'].get('unique_categories', 1000) < 20:
                top_cats = list(metrics['distribution'].get('top_categories', {}).keys())[:10]
                if top_cats:
                    rules.append({
                        'column': col,
                        'rule_type': 'DOMAIN',
                        'description': f'{col} should be one of allowed values',
                        'sql': f"ALTER TABLE table_name ADD CONSTRAINT chk_{col} CHECK ({col} IN ({', '.join(repr(c) for c in top_cats)}));"
                    })
            
            # Email validation
            if col_type == 'EMAIL':
                rules.append({
                    'column': col,
                    'rule_type': 'FORMAT',
                    'description': f'{col} should match valid email format',
                    'sql': f"ALTER TABLE table_name ADD CONSTRAINT chk_{col} CHECK ({col} ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{{2,}}$');"
                })
        
        # Display rules
        print("\n📋 Recommended Rules:")
        for i, rule in enumerate(rules, 1):
            print(f"\n{i}. {rule['description']}")
            print(f"   Type: {rule['rule_type']}")
            print(f"   SQL: {rule['sql']}")
        
        return rules
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate executive summary."""
        print("\n" + "="*80)
        print("4. EXECUTIVE SUMMARY")
        print("="*80)
        
        # Calculate overall score
        self.overall_score = statistics.mean(self.quality_scores.values()) if self.quality_scores else 0
        
        # Identify main issues
        issues = []
        high_null_cols = [col for col, metrics in self.quality_metrics.items() 
                         if metrics['null_percentage'] > 20]
        if high_null_cols:
            issues.append(f"High null percentages in: {', '.join(high_null_cols)}")
        
        format_issue_cols = [col for col, metrics in self.quality_metrics.items() 
                           if metrics['format_issues']]
        if format_issue_cols:
            issues.append(f"Format inconsistencies in: {', '.join(format_issue_cols)}")
        
        outlier_cols = [col for col, metrics in self.quality_metrics.items() 
                       if metrics['outliers']]
        if outlier_cols:
            issues.append(f"Outliers detected in: {', '.join(outlier_cols)}")
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        summary = {
            'overall_score': self.overall_score,
            'column_scores': self.quality_scores,
            'main_issues': issues,
            'recommendations': recommendations
        }
        
        # Display summary
        score_indicator = '✅' if self.overall_score >= 4 else '⚠️' if self.overall_score >= 3 else '❌'
        print(f"\n{score_indicator} Overall Quality Score: {self.overall_score:.2f}/5.0")
        
        print("\n📊 Column Scores:")
        for col, score in sorted(self.quality_scores.items(), key=lambda x: x[1]):
            indicator = '✅' if score >= 4 else '⚠️' if score >= 3 else '❌'
            print(f"   {indicator} {col}: {score:.1f}/5.0")
        
        print("\n⚠️  Main Issues:")
        if issues:
            for issue in issues:
                print(f"   • {issue}")
        else:
            print("   ✅ No major issues detected")
        
        print("\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   • {rec}")
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate specific recommendations."""
        recommendations = []
        
        for col, metrics in self.quality_metrics.items():
            # Recommendations for high null percentage
            if metrics['null_percentage'] > 20:
                recommendations.append(
                    f"Investigate and handle missing values in '{col}' (consider imputation, default values, or making it optional)"
                )
            
            # Recommendations for format issues
            if metrics['format_issues']:
                recommendations.append(
                    f"Standardize format for '{col}' - implement validation at data entry point"
                )
            
            # Recommendations for outliers
            if metrics['outliers']:
                recommendations.append(
                    f"Review and validate outliers in '{col}' - may indicate data entry errors or special cases"
                )
            
            # Recommendations for high duplicates in potential key fields
            if metrics['duplicate_percentage'] > 80 and self.column_types[col] not in ['BOOLEAN']:
                recommendations.append(
                    f"High duplicate rate in '{col}' - verify if this is expected or consider data enrichment"
                )
        
        # General recommendations
        if not any('PRIMARY KEY' in str(rule) for rule in self._get_structure_info().get('possible_keys', [])):
            recommendations.append(
                "Add a primary key or unique identifier column to ensure data integrity"
            )
        
        return recommendations
    
    def _create_action_plan(self) -> Dict[str, List[str]]:
        """Create prioritized action plan."""
        print("\n" + "="*80)
        print("5. ACTION PLAN")
        print("="*80)
        
        action_plan = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'quality_kpis': [],
            'roadmap': []
        }
        
        # Critical priority - data integrity issues
        for col, metrics in self.quality_metrics.items():
            if metrics['null_percentage'] > 50:
                action_plan['critical'].append(
                    f"Address critical data gaps in '{col}' ({metrics['null_percentage']:.1f}% null)"
                )
            
            if metrics['format_issues'] and self.column_types[col] in ['EMAIL', 'DATE']:
                action_plan['critical'].append(
                    f"Fix invalid {self.column_types[col]} formats in '{col}'"
                )
        
        # High priority - data quality issues
        for col, metrics in self.quality_metrics.items():
            if 20 < metrics['null_percentage'] <= 50:
                action_plan['high'].append(
                    f"Reduce missing values in '{col}' (currently {metrics['null_percentage']:.1f}%)"
                )
            
            if metrics['outliers']:
                action_plan['high'].append(
                    f"Investigate and validate {len(metrics['outliers'])} outliers in '{col}'"
                )
        
        # Medium priority - standardization
        for col, metrics in self.quality_metrics.items():
            if metrics['format_issues'] and self.column_types[col] not in ['EMAIL', 'DATE']:
                action_plan['medium'].append(
                    f"Standardize text format in '{col}'"
                )
            
            if 5 < metrics['null_percentage'] <= 20:
                action_plan['medium'].append(
                    f"Improve completeness of '{col}' (currently {metrics['null_percentage']:.1f}% null)"
                )
        
        # Low priority - enhancements
        low_score_cols = [col for col, score in self.quality_scores.items() if 3 <= score < 4]
        for col in low_score_cols:
            action_plan['low'].append(
                f"Enhance data quality for '{col}' (score: {self.quality_scores[col]:.1f}/5)"
            )
        
        # Quality KPIs
        action_plan['quality_kpis'] = [
            f"Track null percentage per column (target: <5%)",
            f"Monitor duplicate rates in key columns (target: <10%)",
            f"Measure format compliance (target: 100%)",
            f"Track overall quality score (target: >4.0)",
            f"Monitor outlier detection rate (review threshold quarterly)"
        ]
        
        # Roadmap
        action_plan['roadmap'] = [
            "Week 1-2: Address all critical priority items",
            "Week 3-4: Implement high priority fixes and validations",
            "Month 2: Standardize formats and complete medium priority items",
            "Month 3: Enhance data quality and implement low priority improvements",
            "Ongoing: Monitor KPIs and maintain data quality standards"
        ]
        
        # Display action plan
        print("\n🔴 CRITICAL PRIORITY (Immediate Action Required):")
        if action_plan['critical']:
            for item in action_plan['critical']:
                print(f"   ❌ {item}")
        else:
            print("   ✅ No critical issues")
        
        print("\n🟠 HIGH PRIORITY (1-2 Weeks):")
        if action_plan['high']:
            for item in action_plan['high']:
                print(f"   ⚠️  {item}")
        else:
            print("   ✅ No high priority issues")
        
        print("\n🟡 MEDIUM PRIORITY (1 Month):")
        if action_plan['medium']:
            for item in action_plan['medium']:
                print(f"   • {item}")
        else:
            print("   ✅ No medium priority issues")
        
        print("\n🟢 LOW PRIORITY (Continuous Improvement):")
        if action_plan['low']:
            for item in action_plan['low']:
                print(f"   • {item}")
        else:
            print("   ✅ No low priority issues")
        
        print("\n📊 Quality KPIs to Monitor:")
        for kpi in action_plan['quality_kpis']:
            print(f"   • {kpi}")
        
        print("\n🗓️  Implementation Roadmap:")
        for milestone in action_plan['roadmap']:
            print(f"   • {milestone}")
        
        return action_plan
    
    def _get_structure_info(self) -> Dict[str, Any]:
        """Get structure information."""
        return {
            'columns': self.columns,
            'column_types': self.column_types,
            'column_max_lengths': self.column_max_lengths,
            'possible_keys': self._identify_keys(),
            'total_rows': len(self.data)
        }
    
    def export_report(self, output_file: str = 'data_quality_report.json'):
        """Export analysis report to JSON file."""
        report = {
            'data_source': self.data_source,
            'analysis_date': datetime.now().isoformat(),
            'structure': self._get_structure_info(),
            'quality_metrics': self.quality_metrics,
            'quality_scores': self.quality_scores,
            'overall_score': self.overall_score
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n✅ Report exported to: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Comprehensive Data Quality Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data.csv
  %(prog)s sales_data.csv --export report.json
  
The tool will analyze the data and provide:
  1. Structure identification (columns, types, keys)
  2. Quality metrics (nulls, duplicates, distributions)
  3. Data quality rules recommendations
  4. Executive summary with scores
  5. Prioritized action plan
        """
    )
    
    parser.add_argument(
        'data_source',
        help='Path to CSV file or database table name'
    )
    
    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export detailed report to JSON file'
    )
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = DataQualityAnalyzer(args.data_source)
    
    # Load data
    if not analyzer.load_data():
        sys.exit(1)
    
    # Perform analysis
    try:
        results = analyzer.analyze()
        
        # Export if requested
        if args.export:
            analyzer.export_report(args.export)
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
