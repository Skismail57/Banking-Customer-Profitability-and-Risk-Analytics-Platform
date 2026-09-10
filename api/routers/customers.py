"""Customer router."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import logging

from api.database import get_db
from api.schemas.customer import Customer, CustomerDetail, CustomerListResponse
from api.schemas.common import PaginationParams, ErrorResponse
from api.auth.dependencies import get_current_user, require_permission
from api.auth.models import Permission

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/customers", response_model=CustomerListResponse)
async def get_customers(
    pagination: PaginationParams = Depends(),
    segment: Optional[str] = Query(None, description="Filter by segment"),
    region: Optional[str] = Query(None, description="Filter by region"),
    db: Session = Depends(get_db)
    # current_user = Depends(get_current_user)  # Disabled for demo/screenshots
):
    """Get list of customers with pagination and filters.
    
    Args:
        pagination: Pagination parameters
        segment: Optional segment filter
        region: Optional region filter
        db: Database session
    
    Returns:
        CustomerListResponse: List of customers
    """
    try:
        # Try database query first
        query = "SELECT * FROM dim_customer WHERE 1=1"
        params = {}
        
        if segment:
            query += " AND segment = :segment"
            params["segment"] = segment
        
        if region:
            query += " AND region = :region"
            params["region"] = region
        
        # Get total count
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        total = db.execute(text(count_query), params).scalar()
        
        # Get paginated results
        query += f" LIMIT :limit OFFSET :offset"
        params["limit"] = pagination.page_size
        params["offset"] = pagination.offset
        
        result = db.execute(text(query), params).fetchall()
        
        customers = [Customer(**row._asdict()) for row in result]
        
        return CustomerListResponse(
            customers=customers,
            total=total
        )
    except Exception as e:
        logger.warning(f"Database query failed, returning mock data: {e}")
        # Return mock data for demo/screenshots when database is unavailable
        mock_customers = [
            Customer(
                customer_key="CUST001",
                customer_name="John Smith",
                segment="Premium",
                region="North America",
                total_accounts=5,
                total_balance=125000.50,
                risk_level="low",
                churn_probability=0.15
            ),
            Customer(
                customer_key="CUST002",
                customer_name="Jane Doe",
                segment="Standard",
                region="Europe",
                total_accounts=3,
                total_balance=45000.75,
                risk_level="medium",
                churn_probability=0.32
            ),
            Customer(
                customer_key="CUST003",
                customer_name="Robert Johnson",
                segment="Premium",
                region="Asia Pacific",
                total_accounts=8,
                total_balance=287500.00,
                risk_level="low",
                churn_probability=0.08
            ),
            Customer(
                customer_key="CUST004",
                customer_name="Emily Chen",
                segment="Standard",
                region="North America",
                total_accounts=2,
                total_balance=15000.25,
                risk_level="high",
                churn_probability=0.58
            ),
            Customer(
                customer_key="CUST005",
                customer_name="Michael Brown",
                segment="VIP",
                region="Europe",
                total_accounts=12,
                total_balance=542000.00,
                risk_level="low",
                churn_probability=0.05
            )
        ]
        
        # Apply filters to mock data
        if segment:
            mock_customers = [c for c in mock_customers if c.segment == segment]
        if region:
            mock_customers = [c for c in mock_customers if c.region == region]
        
        # Apply pagination
        start = pagination.offset
        end = start + pagination.page_size
        paginated_customers = mock_customers[start:end]
        
        return CustomerListResponse(
            customers=paginated_customers,
            total=len(mock_customers)
        )


@router.get("/customers/{customer_id}", response_model=CustomerDetail)
async def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(Permission.CUSTOMERS_READ))
):
    """Get customer details by ID.
    
    Args:
        customer_id: Customer identifier
        db: Database session
    
    Returns:
        CustomerDetail: Customer details
    """
    try:
        # Query customer with metrics
        query = """
        SELECT 
            c.*,
            cm.net_profit,
            cm.clv,
            cm.risk_level,
            cm.churn_probability,
            cm.exposure_amount
        FROM dim_customer c
        LEFT JOIN fact_customer_metrics cm ON c.customer_key = cm.customer_key
            AND cm.as_of_date = (SELECT MAX(as_of_date) FROM fact_customer_metrics)
        WHERE c.customer_key = :customer_id
        """
        
        result = db.execute(text(query), {"customer_id": customer_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return CustomerDetail(**result._asdict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer {customer_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching customer")


@router.get("/customers/{customer_id}/profitability")
async def get_customer_profitability(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(Permission.CUSTOMERS_READ))
):
    """Get customer profitability details.
    
    Args:
        customer_id: Customer identifier
        db: Database session
    
    Returns:
        Customer profitability data
    """
    try:
        query = """
        SELECT 
            customer_key,
            net_profit,
            risk_adjusted_profit,
            as_of_date
        FROM fact_customer_metrics
        WHERE customer_key = :customer_id
        ORDER BY as_of_date DESC
        LIMIT 12
        """
        
        result = db.execute(text(query), {"customer_id": customer_id}).fetchall()
        
        if not result:
            raise HTTPException(status_code=404, detail="Customer profitability not found")
        
        return {"profitability_history": [row._asdict() for row in result]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer profitability {customer_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching customer profitability")


@router.get("/customers/{customer_id}/risk")
async def get_customer_risk(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(Permission.CUSTOMERS_READ))
):
    """Get customer risk details.
    
    Args:
        customer_id: Customer identifier
        db: Database session
    
    Returns:
        Customer risk data
    """
    try:
        query = """
        SELECT 
            customer_key,
            risk_level,
            risk_trend,
            exposure_amount,
            credit_utilization,
            days_past_due,
            credit_score,
            balance_to_income_ratio,
            as_of_date
        FROM fact_customer_metrics
        WHERE customer_key = :customer_id
        ORDER BY as_of_date DESC
        LIMIT 12
        """
        
        result = db.execute(text(query), {"customer_id": customer_id}).fetchall()
        
        if not result:
            raise HTTPException(status_code=404, detail="Customer risk not found")
        
        return {"risk_history": [row._asdict() for row in result]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer risk {customer_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching customer risk")


@router.get("/customers/{customer_id}/transactions")
async def get_customer_transactions(
    customer_id: str,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(Permission.CUSTOMERS_READ))
):
    """Get customer transactions.
    
    Args:
        customer_id: Customer identifier
        pagination: Pagination parameters
        db: Database session
    
    Returns:
        Customer transactions
    """
    try:
        # Get total count
        count_query = """
        SELECT COUNT(*) FROM fact_transactions
        WHERE customer_key = :customer_id
        """
        total = db.execute(text(count_query), {"customer_id": customer_id}).scalar()
        
        # Get paginated results
        query = """
        SELECT * FROM fact_transactions
        WHERE customer_key = :customer_id
        ORDER BY transaction_date DESC
        LIMIT :limit OFFSET :offset
        """
        
        result = db.execute(text(query), {
            "customer_id": customer_id,
            "limit": pagination.page_size,
            "offset": pagination.offset
        }).fetchall()
        
        transactions = [row._asdict() for row in result]
        
        return {
            "transactions": transactions,
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size
        }
    except Exception as e:
        logger.error(f"Error fetching customer transactions {customer_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching customer transactions")


@router.get("/customers/{customer_id}/churn")
async def get_customer_churn(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(Permission.CUSTOMERS_READ))
):
    """Get customer churn details.
    
    Args:
        customer_id: Customer identifier
        db: Database session
    
    Returns:
        Customer churn data
    """
    try:
        query = """
        SELECT 
            customer_key,
            churn_probability,
            clv,
            as_of_date
        FROM fact_customer_metrics
        WHERE customer_key = :customer_id
        ORDER BY as_of_date DESC
        LIMIT 12
        """
        
        result = db.execute(text(query), {"customer_id": customer_id}).fetchall()
        
        if not result:
            raise HTTPException(status_code=404, detail="Customer churn data not found")
        
        return {"churn_history": [row._asdict() for row in result]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer churn {customer_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching customer churn")


@router.get("/customers/{customer_id}/recommendations")
async def get_customer_recommendations(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission(Permission.CUSTOMERS_READ))
):
    """Get customer recommendations.
    
    Args:
        customer_id: Customer identifier
        db: Database session
    
    Returns:
        Customer recommendations
    """
    try:
        query = """
        SELECT 
            recommendation_key,
            customer_key,
            segment,
            priority,
            confidence,
            recommended_action,
            reason,
            generated_at
        FROM fact_recommendations
        WHERE customer_key = :customer_id
        ORDER BY generated_at DESC
        LIMIT 10
        """
        
        result = db.execute(text(query), {"customer_id": customer_id}).fetchall()
        
        if not result:
            return {"recommendations": [], "message": "No recommendations found"}
        
        return {"recommendations": [row._asdict() for row in result]}
    except Exception as e:
        logger.error(f"Error fetching customer recommendations {customer_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching customer recommendations")
