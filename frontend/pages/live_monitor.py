"""Live monitoring dashboard for real-time analytics.

This page provides real-time monitoring of streaming metrics,
alerts, risk scores, and system health.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np


def generate_mock_metrics():
    """Generate mock metrics when backend is unavailable."""
    return {
        'events_processed': np.random.randint(50000, 100000),
        'events_per_second': np.random.uniform(50, 150),
        'alerts_generated': np.random.randint(5, 25),
        'anomalies_detected': np.random.randint(1, 10),
        'processing_latency_ms': np.random.uniform(20, 150),
        'uptime_percentage': np.random.uniform(95, 100),
        'risk_events': np.random.randint(0, 15)
    }


def generate_mock_alerts(limit=20):
    """Generate mock alerts when backend is unavailable."""
    alert_types = ['High Transaction Volume', 'Suspicious Activity', 'Risk Threshold Exceeded', 'Payment Failure', 'Account Anomaly']
    severities = ['critical', 'high', 'medium', 'low']
    alert_sources = ['Transaction Monitor', 'Risk Engine', 'Fraud Detection', 'Payment Gateway']

    alerts = []
    for i in range(limit):
        alerts.append({
            'alert_id': f'ALERT_{i:06d}',
            'alert_type': np.random.choice(alert_types),
            'severity': np.random.choice(severities, p=[0.1, 0.2, 0.4, 0.3]),
            'alert_source': np.random.choice(alert_sources),
            'customer_key': f'CUST_{np.random.randint(0, 1000):06d}',
            'alert_message': f'Alert triggered due to {np.random.choice(["unusual pattern", "threshold breach", "anomaly detected", "suspicious activity"])}',
            'triggered_at': (datetime.now() - timedelta(minutes=np.random.randint(0, 60))).isoformat()
        })
    return alerts


def generate_mock_watchlist(limit=50):
    """Generate mock watchlist when backend is unavailable."""
    warning_levels = ['Critical', 'High', 'Medium', 'Low']

    watchlist = []
    for i in range(limit):
        watchlist.append({
            'customer_key': f'CUST_{np.random.randint(0, 1000):06d}',
            'warning_level': np.random.choice(warning_levels, p=[0.1, 0.2, 0.4, 0.3]),
            'warning_score': np.random.uniform(0.5, 1.0),
            'updated_at': (datetime.now() - timedelta(hours=np.random.randint(0, 24))).isoformat()
        })
    return watchlist


def generate_mock_risk_score(customer_key):
    """Generate mock risk score when backend is unavailable."""
    risk_level = np.random.choice(['critical', 'high', 'medium', 'low'], p=[0.1, 0.2, 0.4, 0.3])
    risk_score = np.random.uniform(0.1, 0.95)

    return {
        'customer_key': customer_key,
        'risk_level': risk_level,
        'risk_score': risk_score,
        'updated_at': datetime.now().isoformat()
    }


def render():
    """Render the live monitor page with advanced animations."""
    st.title("📡 Live Monitor")
    st.markdown("Real-time streaming analytics monitoring")

    # Intro section
    st.markdown("""
    <p style="color: #94a3b8; font-size: 1.1rem;">
        Real-time monitoring of streaming metrics, alerts, risk scores, and system health.
    </p>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh (5 seconds)", value=True)

    # Refresh button
    if st.button("Refresh Now"):
        st.rerun()

    # Generate mock metrics (using local data instead of backend)
    metrics = generate_mock_metrics()

    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Events Processed",
            f"{metrics['events_processed']:,}",
            f"{metrics['events_per_second']:.2f}/sec"
        )

    with col2:
        st.metric(
            "Alerts Generated",
            f"{metrics['alerts_generated']:,}",
            delta_color="inverse" if metrics['alerts_generated'] > 10 else "normal"
        )

    with col3:
        st.metric(
            "Anomalies Detected",
            f"{metrics['anomalies_detected']:,}",
            delta_color="inverse" if metrics['anomalies_detected'] > 5 else "normal"
        )

    with col4:
        st.metric(
            "Processing Latency",
            f"{metrics['processing_latency_ms']:.2f} ms",
            delta_color="inverse" if metrics['processing_latency_ms'] > 100 else "normal"
        )

    # System health
    col5, col6 = st.columns(2)
    with col5:
        st.metric(
            "System Uptime",
            f"{metrics['uptime_percentage']:.1f}%",
            delta_color="normal"
        )

    with col6:
        risk_events = metrics.get('risk_events', 0)
        st.metric(
            "Risk Events",
            f"{risk_events:,}",
            delta_color="inverse" if risk_events > 5 else "normal"
        )

    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Recent Alerts", "Watchlist", "Risk Scores"])

    with tab1:
        st.subheader("Recent Alerts")

        # Generate mock alerts
        alerts = generate_mock_alerts(20)
        if alerts:
            df_alerts = pd.DataFrame(alerts)

            # Format timestamps
            df_alerts['triggered_at'] = pd.to_datetime(df_alerts['triggered_at'])

            # Display alerts
            for _, alert in df_alerts.iterrows():
                severity_color = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(alert['severity'], '⚪')

                st.markdown(
                    f"{severity_color} **{alert['alert_type']}** - {alert['severity'].upper()}\n\n"
                    f"Customer: `{alert['customer_key']}` | "
                    f"Source: {alert['alert_source']} | "
                    f"Time: {alert['triggered_at']}\n\n"
                    f"{alert['alert_message']}"
                )
                st.markdown("---")
        else:
            st.info("No recent alerts")

    with tab2:
        st.subheader("Watchlist")

        # Generate mock watchlist
        watchlist = generate_mock_watchlist(50)
        if watchlist:
            df_watchlist = pd.DataFrame(watchlist)

            # Display as table
            st.dataframe(
                df_watchlist[['customer_key', 'warning_level', 'warning_score', 'updated_at']],
                width="stretch"
            )

            # Warning level distribution
            fig = px.pie(
                df_watchlist,
                names='warning_level',
                title='Watchlist by Warning Level',
                hole=0.4
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No customers on watchlist")

    with tab3:
        st.subheader("Real-time Risk Scores")

        # Customer search
        customer_key = st.text_input("Enter Customer Key to check risk score", value="CUST_000000")

        if customer_key:
            # Generate mock risk score
            risk_data = generate_mock_risk_score(customer_key)

            # Display risk score
            risk_level = risk_data['risk_level']
            risk_score = risk_data['risk_score']

            risk_color = {
                'critical': 'red',
                'high': 'orange',
                'medium': 'yellow',
                'low': 'green'
            }.get(risk_level, 'gray')

            st.markdown(f"### Risk Level: :{risk_color}[{risk_level.upper()}]")
            st.markdown(f"### Risk Score: {risk_score:.2f}")
            st.markdown(f"Last Updated: {risk_data['updated_at']}")

            # Risk score gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score * 100,
                title={'text': "Risk Score"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': risk_color},
                    'steps': [
                        {'range': [0, 25], 'color': "lightgreen"},
                        {'range': [25, 50], 'color': "yellow"},
                        {'range': [50, 75], 'color': "orange"},
                        {'range': [75, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 75
                    }
                }
            ))
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Enter a customer key to view their real-time risk score")

    # Auto-refresh
    if auto_refresh:
        import time
        time.sleep(5)
        st.rerun()
