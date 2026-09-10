"""Data validator for streaming pipeline.

This module provides data validation capabilities to ensure data quality
in the streaming pipeline.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class ValidationRule(Enum):
    """Types of validation rules."""
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    RANGE = "range"
    REGEX = "regex"
    ENUM = "enum"
    CUSTOM = "custom"


@dataclass
class ValidationResult:
    """Data validation result."""
    validation_id: str
    rule_type: str
    field: str
    passed: bool
    message: str
    failed_count: int
    total_count: int
    validated_at: datetime


class DataValidator:
    """Data validator for quality checks."""
    
    def __init__(self):
        """Initialize data validator."""
        self.validation_rules = {}
        self.validation_history = []
    
    def add_rule(
        self,
        rule_name: str,
        rule_type: ValidationRule,
        field: str,
        parameters: Optional[Dict[str, Any]] = None,
        custom_function: Optional[Callable] = None
    ):
        """Add a validation rule.
        
        Args:
            rule_name: Name of the rule
            rule_type: Type of validation rule
            field: Field to validate
            parameters: Rule parameters
            custom_function: Custom validation function
        """
        self.validation_rules[rule_name] = {
            'rule_type': rule_type,
            'field': field,
            'parameters': parameters or {},
            'custom_function': custom_function
        }
    
    def validate_data(self, data: pd.DataFrame) -> List[ValidationResult]:
        """Validate data against all rules.
        
        Args:
            data: Data to validate
        
        Returns:
            List of validation results
        """
        results = []
        
        for rule_name, rule_config in self.validation_rules.items():
            result = self._apply_rule(rule_name, rule_config, data)
            results.append(result)
            self.validation_history.append(result)
        
        return results
    
    def _apply_rule(
        self,
        rule_name: str,
        rule_config: Dict[str, Any],
        data: pd.DataFrame
    ) -> ValidationResult:
        """Apply a single validation rule.
        
        Args:
            rule_name: Name of the rule
            rule_config: Rule configuration
            data: Data to validate
        
        Returns:
            Validation result
        """
        validation_id = f"validation_{int(datetime.utcnow().timestamp())}"
        rule_type = rule_config['rule_type']
        field = rule_config['field']
        parameters = rule_config['parameters']
        
        total_count = len(data)
        failed_count = 0
        passed = True
        message = ""
        
        try:
            if rule_type == ValidationRule.NOT_NULL:
                failed_count = data[field].isna().sum()
                passed = failed_count == 0
                message = f"Null check for {field}: {failed_count} null values"
            
            elif rule_type == ValidationRule.UNIQUE:
                failed_count = data[field].duplicated().sum()
                passed = failed_count == 0
                message = f"Uniqueness check for {field}: {failed_count} duplicates"
            
            elif rule_type == ValidationRule.RANGE:
                min_val = parameters.get('min')
                max_val = parameters.get('max')
                failed_count = ((data[field] < min_val) | (data[field] > max_val)).sum()
                passed = failed_count == 0
                message = f"Range check for {field}: {failed_count} values outside [{min_val}, {max_val}]"
            
            elif rule_type == ValidationRule.REGEX:
                import re
                pattern = parameters.get('pattern')
                failed_count = ~data[field].str.match(pattern, na=False).sum()
                passed = failed_count == 0
                message = f"Regex check for {field}: {failed_count} values don't match pattern"
            
            elif rule_type == ValidationRule.ENUM:
                allowed_values = parameters.get('allowed_values', [])
                failed_count = (~data[field].isin(allowed_values)).sum()
                passed = failed_count == 0
                message = f"Enum check for {field}: {failed_count} values not in allowed set"
            
            elif rule_type == ValidationRule.CUSTOM:
                custom_function = rule_config['custom_function']
                result = custom_function(data[field])
                failed_count = result['failed_count']
                passed = result['passed']
                message = result.get('message', f"Custom validation for {field}")
        
        except Exception as e:
            logger.error(f"Error applying rule {rule_name}: {e}")
            passed = False
            message = f"Validation error: {str(e)}"
        
        return ValidationResult(
            validation_id=validation_id,
            rule_type=rule_type.value,
            field=field,
            passed=passed,
            message=message,
            failed_count=failed_count,
            total_count=total_count,
            validated_at=datetime.utcnow()
        )
    
    def validate_field(
        self,
        data: pd.DataFrame,
        field: str,
        rule_type: ValidationRule,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate a single field.
        
        Args:
            data: Data to validate
            field: Field to validate
            rule_type: Type of validation
            parameters: Rule parameters
        
        Returns:
            Validation result
        """
        rule_config = {
            'rule_type': rule_type,
            'field': field,
            'parameters': parameters or {}
        }
        
        return self._apply_rule(f"field_{field}", rule_config, data)
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary.
        
        Returns:
            Validation summary
        """
        if not self.validation_history:
            return {'message': 'No validations performed'}
        
        total = len(self.validation_history)
        passed = sum(1 for v in self.validation_history if v.passed)
        failed = total - passed
        
        return {
            'total_validations': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': passed / total if total > 0 else 0,
            'by_rule_type': self._summarize_by_rule_type()
        }
    
    def _summarize_by_rule_type(self) -> Dict[str, Dict[str, int]]:
        """Summarize validations by rule type.
        
        Returns:
            Summary by rule type
        """
        summary = {}
        
        for validation in self.validation_history:
            rule_type = validation.rule_type
            if rule_type not in summary:
                summary[rule_type] = {'passed': 0, 'failed': 0}
            
            if validation.passed:
                summary[rule_type]['passed'] += 1
            else:
                summary[rule_type]['failed'] += 1
        
        return summary
