"""Decision Engine - Integrated with ML Outputs.

This module integrates the Decision Engine with ML outputs to generate
actionable recommendations answering "WHAT SHOULD WE DO?"

Architecture Position:
ML (Churn/CLV, Risk Models) → Decision Engine → Power BI/Streamlit/API
"""

from typing import Dict, Any, Optional, List
from datetime import date
import logging

import pandas as pd

from src.data_platform.data_loader import DataLoader
from src.decision_intelligence.rules_engine import RulesEngine
from src.decision_intelligence.base import DecisionBase, Recommendation, Priority, ConfidenceLevel
from src.ml.integrated import IntegratedMLLayer

logger = logging.getLogger(__name__)


class DecisionEngine(DecisionBase):
    """Decision Engine that generates actionable recommendations.
    
    This class integrates ML predictions with business rules to generate
    recommendations for customers and segments.
    """
    
    def __init__(
        self,
        as_of_date: Optional[date] = None,
        data_loader: Optional[DataLoader] = None,
        ml_layer: Optional[IntegratedMLLayer] = None
    ):
        """Initialize Decision Engine.
        
        Args:
            as_of_date: As-of date for decision generation
            data_loader: Data loader instance
            ml_layer: ML layer instance
        """
        self.as_of_date = as_of_date or date.today()
        self.data_loader = data_loader or DataLoader()
        self.ml_layer = ml_layer or IntegratedMLLayer(as_of_date=self.as_of_date)
        
        # Initialize rules engine
        self.rules_engine = RulesEngine()
        
        # Register decision rules
        self._register_decision_rules()
    
    def _register_decision_rules(self) -> None:
        """Register decision rules based on ML outputs and business logic."""
        
        # High churn risk rule
        self.rules_engine.register_rule(
            rule_name="high_churn_risk",
            condition=lambda data: data.get('churn_probability', 0) > 0.7,
            action_generator=lambda data: {
                'triggering_metrics': {'churn_probability': data.get('churn_probability')},
                'reason': f"Customer has high churn risk ({data.get('churn_probability', 0):.1%})",
                'recommended_action': "Implement retention campaign: offer loyalty incentives, personalized outreach, and service improvements",
                'priority': Priority.HIGH,
                'confidence': ConfidenceLevel.HIGH,
                'limitations': ['Based on historical patterns', 'May not account for recent life events']
            }
        )
        
        # High risk level rule
        self.rules_engine.register_rule(
            rule_name="high_risk_level",
            condition=lambda data: data.get('risk_level') in ['high', 'critical'],
            action_generator=lambda data: {
                'triggering_metrics': {'risk_level': data.get('risk_level'), 'credit_utilization': data.get('credit_utilization')},
                'reason': f"Customer has {data.get('risk_level')} risk level with {data.get('credit_utilization', 0):.1%} credit utilization",
                'recommended_action': "Implement risk mitigation: reduce credit limits, increase monitoring, offer debt counseling",
                'priority': Priority.HIGH,
                'confidence': ConfidenceLevel.HIGH,
                'limitations': ['Risk assessment based on current snapshot', 'May not reflect recent payments']
            }
        )
        
        # Low profitability rule
        self.rules_engine.register_rule(
            rule_name="low_profitability",
            condition=lambda data: data.get('net_profit', 0) < 0,
            action_generator=lambda data: {
                'triggering_metrics': {'net_profit': data.get('net_profit')},
                'reason': f"Customer is unprofitable with net profit of ${data.get('net_profit', 0):,.2f}",
                'recommended_action': "Review account profitability: consider fee adjustments, cross-sell opportunities, or account closure",
                'priority': Priority.MEDIUM,
                'confidence': ConfidenceLevel.MEDIUM,
                'limitations': ['Profitability may be temporary', 'Does not account for long-term value']
            }
        )
        
        # High CLV opportunity rule
        self.rules_engine.register_rule(
            rule_name="high_clv_opportunity",
            condition=lambda data: data.get('clv', 0) > 10000,
            action_generator=lambda data: {
                'triggering_metrics': {'clv': data.get('clv')},
                'reason': f"Customer has high CLV of ${data.get('clv', 0):,.2f}",
                'recommended_action': "Prioritize relationship: offer premium services, dedicated support, and exclusive benefits",
                'priority': Priority.HIGH,
                'confidence': ConfidenceLevel.HIGH,
                'limitations': ['CLV is a projection', 'Actual value may vary']
            }
        )
        
        # Cross-sell opportunity rule
        self.rules_engine.register_rule(
            rule_name="cross_sell_opportunity",
            condition=lambda data: data.get('segment') == 'premium' and data.get('product_count', 0) < 3,
            action_generator=lambda data: {
                'triggering_metrics': {'segment': data.get('segment'), 'product_count': data.get('product_count', 0)},
                'reason': f"Premium customer with only {data.get('product_count', 0)} products",
                'recommended_action': "Cross-sell premium products: investment accounts, premium credit cards, wealth management services",
                'priority': Priority.MEDIUM,
                'confidence': ConfidenceLevel.MEDIUM,
                'limitations': ['Customer may not be interested', 'Competitive products may be preferred']
            }
        )
        
        # Credit utilization warning rule
        self.rules_engine.register_rule(
            rule_name="high_credit_utilization",
            condition=lambda data: data.get('credit_utilization', 0) > 0.8,
            action_generator=lambda data: {
                'triggering_metrics': {'credit_utilization': data.get('credit_utilization')},
                'reason': f"Customer has high credit utilization of {data.get('credit_utilization', 0):.1%}",
                'recommended_action': "Send utilization warning: educate on credit impact, offer credit limit increase, provide budgeting tools",
                'priority': Priority.MEDIUM,
                'confidence': ConfidenceLevel.HIGH,
                'limitations': ['High utilization may be intentional', 'Does not indicate financial distress']
            }
        )
        
        # Days past due warning rule
        self.rules_engine.register_rule(
            rule_name="days_past_due_warning",
            condition=lambda data: data.get('days_past_due', 0) > 30,
            action_generator=lambda data: {
                'triggering_metrics': {'days_past_due': data.get('days_past_due')},
                'reason': f"Customer is {data.get('days_past_due', 0)} days past due",
                'recommended_action': "Initiate collections process: contact customer, offer payment plans, assess hardship options",
                'priority': Priority.HIGH,
                'confidence': ConfidenceLevel.HIGH,
                'limitations': ['May have valid reasons for delay', 'Payment may be in transit']
            }
        )
    
    def generate_customer_recommendations(
        self,
        customer_keys: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Generate recommendations for customers.
        
        Args:
            customer_keys: Optional list of customer keys to generate recommendations for.
                          If None, generates for all customers.
        
        Returns:
            DataFrame with recommendations
        """
        logger.info("Generating customer recommendations")
        
        # Load customer metrics (Core Analytics output + ML predictions)
        metrics_df = self.data_loader.load_customer_metrics(as_of_date=self.as_of_date)
        
        if metrics_df.empty:
            logger.warning("No customer metrics found for recommendation generation")
            return pd.DataFrame()
        
        # Filter by customer keys if provided
        if customer_keys:
            metrics_df = metrics_df[metrics_df['customer_key'].isin(customer_keys)]
        
        # Generate ML predictions
        features_df = self.ml_layer.generate_ml_features(customer_keys=customer_keys)
        
        if not features_df.empty:
            churn_predictions = self.ml_layer.predict_churn(features_df)
            clv_predictions = self.ml_layer.predict_clv(features_df)
            risk_predictions = self.ml_layer.predict_risk(features_df)
            
            # Merge predictions with metrics
            metrics_df = metrics_df.merge(
                churn_predictions[['customer_key', 'churn_probability']],
                on='customer_key',
                how='left'
            )
            metrics_df = metrics_df.merge(
                clv_predictions[['customer_key', 'clv_prediction']],
                on='customer_key',
                how='left'
            )
            metrics_df = metrics_df.merge(
                risk_predictions[['customer_key', 'predicted_risk_level']],
                on='customer_key',
                how='left'
            )
        
        # Generate recommendations for each customer
        recommendations = []
        
        for _, row in metrics_df.iterrows():
            customer_data = row.to_dict()
            
            # Evaluate rules
            customer_recommendations = self.rules_engine.evaluate_rules(
                customer_data=customer_data,
                customer_key=customer_data['customer_key']
            )
            
            for rec in customer_recommendations:
                recommendations.append({
                    'recommendation_key': f"rec_{customer_data['customer_key']}_{len(recommendations)}",
                    'customer_key': customer_data['customer_key'],
                    'segment': customer_data.get('segment'),
                    'priority': rec.priority.value,
                    'confidence_level': rec.confidence.value,
                    'recommended_action': rec.recommended_action,
                    'reason': rec.reason,
                    'triggering_metrics': rec.triggering_metrics,
                    'limitations': rec.limitations,
                    'generated_at': self.as_of_date
                })
        
        recommendations_df = pd.DataFrame(recommendations)
        
        logger.info(f"Generated {len(recommendations_df)} recommendations for {len(metrics_df)} customers")
        return recommendations_df
    
    def generate_segment_recommendations(self) -> Dict[str, List[Recommendation]]:
        """Generate recommendations for segments.
        
        Returns:
            Dictionary of recommendations by segment
        """
        logger.info("Generating segment recommendations")
        
        # Load customer metrics
        metrics_df = self.data_loader.load_customer_metrics(as_of_date=self.as_of_date)
        
        if metrics_df.empty:
            logger.warning("No customer metrics found for segment recommendation generation")
            return {}
        
        # Aggregate by segment
        segment_recommendations = {}
        
        for segment in metrics_df['segment'].unique():
            segment_data = metrics_df[metrics_df['segment'] == segment]
            
            # Calculate segment-level metrics
            avg_churn_prob = segment_data['churn_probability'].mean() if 'churn_probability' in segment_data.columns else 0
            avg_risk_score = segment_data['risk_level'].apply(lambda x: {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}.get(x, 2)).mean()
            total_clv = segment_data['clv'].sum() if 'clv' in segment_data.columns else 0
            
            # Generate segment recommendations
            segment_recs = []
            
            if avg_churn_prob > 0.5:
                segment_recs.append(Recommendation(
                    customer_key=segment,
                    segment=segment,
                    triggering_metrics={'avg_churn_probability': avg_churn_prob},
                    reason=f"Segment {segment} has high average churn probability of {avg_churn_prob:.1%}",
                    recommended_action="Implement segment-wide retention strategy: targeted marketing, loyalty programs, service improvements",
                    priority=Priority.HIGH,
                    confidence=ConfidenceLevel.HIGH,
                    limitations=['Based on segment average', 'Individual variation exists'],
                    generated_at=self.as_of_date
                ))
            
            if avg_risk_score > 2.5:
                segment_recs.append(Recommendation(
                    customer_key=segment,
                    segment=segment,
                    triggering_metrics={'avg_risk_score': avg_risk_score},
                    reason=f"Segment {segment} has high average risk score of {avg_risk_score:.2f}",
                    recommended_action="Implement segment-wide risk management: stricter underwriting, increased monitoring, portfolio rebalancing",
                    priority=Priority.HIGH,
                    confidence=ConfidenceLevel.HIGH,
                    limitations=['Based on segment average', 'Individual variation exists'],
                    generated_at=self.as_of_date
                ))
            
            if total_clv > 1000000:
                segment_recs.append(Recommendation(
                    customer_key=segment,
                    segment=segment,
                    triggering_metrics={'total_clv': total_clv},
                    reason=f"Segment {segment} has high total CLV of ${total_clv:,.2f}",
                    recommended_action="Invest in segment growth: premium offerings, dedicated resources, strategic partnerships",
                    priority=Priority.HIGH,
                    confidence=ConfidenceLevel.HIGH,
                    limitations=['CLV is a projection', 'Market conditions may change'],
                    generated_at=self.as_of_date
                ))
            
            segment_recommendations[segment] = segment_recs
        
        logger.info(f"Generated segment recommendations for {len(segment_recommendations)} segments")
        return segment_recommendations
    
    def persist_recommendations(self, recommendations_df: pd.DataFrame) -> None:
        """Persist recommendations to fact_recommendations table.
        
        Args:
            recommendations_df: DataFrame with recommendations
        """
        logger.info(f"Persisting {len(recommendations_df)} recommendations to fact_recommendations")
        
        # This would use SQLAlchemy to insert into fact_recommendations
        # For now, just log the action
        logger.info("Recommendations persistence would be implemented here")
    
    def get_recommendation_summary(self) -> Dict[str, Any]:
        """Get summary of generated recommendations.
        
        Returns:
            Dictionary with recommendation summary
        """
        logger.info("Getting recommendation summary")
        
        # Load recommendations
        recommendations_df = self.data_loader.load_recommendations(generated_at=self.as_of_date)
        
        if recommendations_df.empty:
            return {
                'total_recommendations': 0,
                'by_priority': {},
                'by_segment': {},
                'by_confidence': {}
            }
        
        summary = {
            'total_recommendations': len(recommendations_df),
            'by_priority': recommendations_df['priority'].value_counts().to_dict(),
            'by_segment': recommendations_df['segment'].value_counts().to_dict(),
            'by_confidence': recommendations_df['confidence_level'].value_counts().to_dict()
        }
        
        logger.info(f"Recommendation summary: {summary}")
        return summary
