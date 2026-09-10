"""SQL tests for view syntax validation."""

import pytest


@pytest.mark.sql
class TestViewSyntax:
    """Tests for SQL view syntax validation."""
    
    def test_executive_overview_view_exists(self):
        """Test that executive overview view file exists."""
        import os
        view_path = "sql/views/vw_executive_overview_kpi.sql"
        assert os.path.exists(view_path), f"View file {view_path} does not exist"
    
    def test_customer_360_view_exists(self):
        """Test that customer 360 view file exists."""
        import os
        view_path = "sql/views/vw_customer_360_detail.sql"
        assert os.path.exists(view_path), f"View file {view_path} does not exist"
    
    def test_profitability_view_exists(self):
        """Test that profitability view file exists."""
        import os
        view_path = "sql/views/vw_profitability_trend.sql"
        assert os.path.exists(view_path), f"View file {view_path} does not exist"
    
    def test_risk_view_exists(self):
        """Test that risk view file exists."""
        import os
        view_path = "sql/views/vw_risk_distribution.sql"
        assert os.path.exists(view_path), f"View file {view_path} does not exist"
    
    def test_segment_view_exists(self):
        """Test that segment view file exists."""
        import os
        view_path = "sql/views/vw_segment_analysis.sql"
        assert os.path.exists(view_path), f"View file {view_path} does not exist"
    
    def test_churn_view_exists(self):
        """Test that churn view file exists."""
        import os
        view_path = "sql/views/vw_churn_retention.sql"
        assert os.path.exists(view_path), f"View file {view_path} does not exist"
    
    def test_product_view_exists(self):
        """Test that product view file exists."""
        import os
        view_path = "sql/views/vw_product_analytics.sql"
        assert os.path.exists(view_path), f"View file {view_path} does not exist"
    
    def test_transaction_view_exists(self):
        """Test that transaction view file exists."""
        import os
        view_path = "sql/views/vw_transaction_analytics.sql"
        assert os.path.exists(view_path), f"View file {view_path} does not exist"
    
    def test_decision_intelligence_view_exists(self):
        """Test that decision intelligence view file exists."""
        import os
        view_path = "sql/views/vw_decision_intelligence.sql"
        assert os.path.exists(view_path), f"View file {view_path} does not exist"
    
    def test_model_monitoring_view_exists(self):
        """Test that model monitoring view file exists."""
        import os
        view_path = "sql/views/vw_model_monitoring.sql"
        assert os.path.exists(view_path), f"View file {view_path} does not exist"
    
    def test_view_has_create_statement(self):
        """Test that views have CREATE OR REPLACE VIEW statement."""
        import os
        view_files = [
            "sql/views/vw_executive_overview_kpi.sql",
            "sql/views/vw_customer_360_detail.sql",
            "sql/views/vw_profitability_trend.sql",
        ]
        
        for view_file in view_files:
            if os.path.exists(view_file):
                with open(view_file, 'r') as f:
                    content = f.read()
                    assert "CREATE OR REPLACE VIEW" in content, \
                        f"View {view_file} missing CREATE OR REPLACE VIEW statement"
    
    def test_view_has_select_statement(self):
        """Test that views have SELECT statement."""
        import os
        view_files = [
            "sql/views/vw_executive_overview_kpi.sql",
            "sql/views/vw_customer_360_detail.sql",
        ]
        
        for view_file in view_files:
            if os.path.exists(view_file):
                with open(view_file, 'r') as f:
                    content = f.read()
                    assert "SELECT" in content, \
                        f"View {view_file} missing SELECT statement"
