"""Regression analysis (linear, logistic)."""

from typing import Dict, Any, List, Optional
import logging

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import r2_score, mean_squared_error
import statsmodels.api as sm

from src.statistical_analytics.base import StatisticalBase, TestResult

logger = logging.getLogger(__name__)


class RegressionAnalyzer(StatisticalBase):
    """Perform regression analysis for relationships between variables."""
    
    def linear_regression(
        self,
        df: pd.DataFrame,
        y_col: str,
        x_cols: List[str]
    ) -> Dict[str, Any]:
        """Perform linear regression.
        
        Args:
            df: DataFrame with data
            y_col: Dependent variable column
            x_cols: Independent variable columns
        
        Returns:
            Dictionary with regression results
        """
        # Prepare data
        df_clean = df[[y_col] + x_cols].dropna()
        X = df_clean[x_cols]
        y = df_clean[y_col]
        
        # Add constant for statsmodels
        X_sm = sm.add_constant(X)
        
        # Fit model with statsmodels for detailed statistics
        model = sm.OLS(y, X_sm).fit()
        
        # Calculate R-squared with sklearn
        sklearn_model = LinearRegression()
        sklearn_model.fit(X, y)
        y_pred = sklearn_model.predict(X)
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        
        # Extract coefficients and p-values
        results = {
            "model_type": "Linear Regression",
            "dependent_variable": y_col,
            "independent_variables": x_cols,
            "r_squared": r2,
            "adjusted_r_squared": model.rsquared_adj,
            "mse": mse,
            "rmse": np.sqrt(mse),
            "f_statistic": model.fvalue,
            "f_p_value": model.f_pvalue,
            "coefficients": [],
            "assumptions": [
                "Linear relationship between variables",
                "Independent observations",
                "Homoscedasticity",
                "Normally distributed residuals",
                "No multicollinearity"
            ]
        }
        
        # Add coefficient details
        for i, col in enumerate(["const"] + x_cols):
            coef = model.params[i]
            p_value = model.pvalues[i]
            conf_int = model.conf_int()[i]
            
            results["coefficients"].append({
                "variable": col,
                "coefficient": coef,
                "std_error": model.bse[i],
                "t_statistic": model.tvalues[i],
                "p_value": p_value,
                "ci_lower": conf_int[0],
                "ci_upper": conf_int[1],
                "significant": p_value < self.alpha
            })
        
        return results
    
    def logistic_regression(
        self,
        df: pd.DataFrame,
        y_col: str,
        x_cols: List[str]
    ) -> Dict[str, Any]:
        """Perform logistic regression.
        
        Args:
            df: DataFrame with data
            y_col: Binary dependent variable column
            x_cols: Independent variable columns
        
        Returns:
            Dictionary with regression results
        """
        # Prepare data
        df_clean = df[[y_col] + x_cols].dropna()
        X = df_clean[x_cols]
        y = df_clean[y_col]
        
        # Add constant for statsmodels
        X_sm = sm.add_constant(X)
        
        # Fit model with statsmodels
        model = sm.Logit(y, X_sm).fit(disp=0)
        
        # Calculate predictions with sklearn
        sklearn_model = LogisticRegression(max_iter=1000)
        sklearn_model.fit(X, y)
        y_pred_proba = sklearn_model.predict_proba(X)[:, 1]
        
        # Extract coefficients and p-values
        results = {
            "model_type": "Logistic Regression",
            "dependent_variable": y_col,
            "independent_variables": x_cols,
            "llf": model.llf,
            "llr": model.llr,
            "llr_pvalue": model.llr_pvalue,
            "pseudo_r_squared": model.prsquared,
            "coefficients": [],
            "assumptions": [
                "Binary dependent variable",
                "Independent observations",
                "No perfect multicollinearity",
                "Large sample size",
                "Linearity of logit"
            ]
        }
        
        # Add coefficient details
        for i, col in enumerate(["const"] + x_cols):
            coef = model.params[i]
            p_value = model.pvalues[i]
            conf_int = model.conf_int()[i]
            odds_ratio = np.exp(coef)
            
            results["coefficients"].append({
                "variable": col,
                "coefficient": coef,
                "std_error": model.bse[i],
                "z_statistic": model.tvalues[i],
                "p_value": p_value,
                "ci_lower": conf_int[0],
                "ci_upper": conf_int[1],
                "odds_ratio": odds_ratio,
                "odds_ratio_ci_lower": np.exp(conf_int[0]),
                "odds_ratio_ci_upper": np.exp(conf_int[1]),
                "significant": p_value < self.alpha
            })
        
        return results
