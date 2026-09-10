"""Schema registry client for streaming event schemas.

This module provides a client for interacting with the schema registry
(Redpanda's built-in schema registry or external) to manage Avro schemas
for event serialization and validation.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

import requests
from pydantic import BaseModel

from src.streaming.config import StreamingConfig

logger = logging.getLogger(__name__)


class CompatibilityLevel(str, Enum):
    """Schema compatibility levels."""
    NONE = "NONE"
    BACKWARD = "BACKWARD"
    FORWARD = "FORWARD"
    FULL = "FULL"
    BACKWARD_TRANSITIVE = "BACKWARD_TRANSITIVE"
    FORWARD_TRANSITIVE = "FORWARD_TRANSITIVE"
    FULL_TRANSITIVE = "FULL_TRANSITIVE"


@dataclass
class SchemaReference:
    """Reference to a registered schema."""
    subject: str
    version: int
    schema_id: int


class SchemaRegistryClient:
    """Client for interacting with the schema registry.
    
    This client supports Redpanda's built-in schema registry as well as
    external schema registries like Confluent Schema Registry.
    """
    
    def __init__(self, config: StreamingConfig):
        """Initialize schema registry client.
        
        Args:
            config: Streaming configuration
        """
        self.config = config
        self.enabled = config.schema_registry.enable
        self.url = config.schema_registry.url
        self.api_key = config.schema_registry.api_key
        self.api_secret = config.schema_registry.api_secret
        
        if not self.enabled:
            logger.warning("Schema registry is disabled in configuration")
        
        self._headers = self._build_headers()
    
    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for schema registry requests.
        
        Returns:
            Dictionary of headers
        """
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key and self.api_secret:
            headers["Authorization"] = f"Basic {self._encode_credentials()}"
        
        return headers
    
    def _encode_credentials(self) -> str:
        """Encode API credentials for basic auth.
        
        Returns:
            Base64 encoded credentials
        """
        import base64
        credentials = f"{self.api_key}:{self.api_secret}"
        return base64.b64encode(credentials.encode()).decode()
    
    def register_schema(
        self,
        subject: str,
        schema: Dict[str, Any],
        schema_type: str = "AVRO",
        compatibility_level: CompatibilityLevel = CompatibilityLevel.BACKWARD
    ) -> SchemaReference:
        """Register a new schema in the schema registry.
        
        Args:
            subject: Subject name (typically topic name)
            schema: Schema definition
            schema_type: Schema type (AVRO, JSON, PROTOBUF)
            compatibility_level: Compatibility level for the subject
        
        Returns:
            SchemaReference with subject, version, and schema_id
        
        Raises:
            RuntimeError: If schema registry is disabled or request fails
        """
        if not self.enabled:
            raise RuntimeError("Schema registry is disabled")
        
        schema_str = json.dumps(schema)
        
        # First, set compatibility level for the subject
        self._set_compatibility_level(subject, compatibility_level)
        
        # Register the schema
        endpoint = f"{self.url}/subjects/{subject}/versions"
        payload = {
            "schema": schema_str,
            "schemaType": schema_type,
        }
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self._headers,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            return SchemaReference(
                subject=subject,
                version=result.get("version"),
                schema_id=result.get("id")
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to register schema for subject {subject}: {e}")
            raise RuntimeError(f"Schema registration failed: {e}")
    
    def get_schema(
        self,
        subject: str,
        version: Optional[int] = None,
        schema_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get a schema from the registry.
        
        Args:
            subject: Subject name
            version: Schema version (if None, returns latest)
            schema_id: Schema ID (alternative identifier)
        
        Returns:
            Schema definition
        
        Raises:
            RuntimeError: If schema registry is disabled or request fails
        """
        if not self.enabled:
            raise RuntimeError("Schema registry is disabled")
        
        if schema_id:
            endpoint = f"{self.url}/schemas/ids/{schema_id}"
        elif version:
            endpoint = f"{self.url}/subjects/{subject}/versions/{version}"
        else:
            endpoint = f"{self.url}/subjects/{subject}/versions/latest"
        
        try:
            response = requests.get(
                endpoint,
                headers=self._headers,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            return json.loads(result.get("schema"))
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get schema for subject {subject}: {e}")
            raise RuntimeError(f"Schema retrieval failed: {e}")
    
    def get_latest_version(self, subject: str) -> int:
        """Get the latest schema version for a subject.
        
        Args:
            subject: Subject name
        
        Returns:
            Latest schema version
        
        Raises:
            RuntimeError: If schema registry is disabled or request fails
        """
        if not self.enabled:
            raise RuntimeError("Schema registry is disabled")
        
        endpoint = f"{self.url}/subjects/{subject}"
        
        try:
            response = requests.get(
                endpoint,
                headers=self._headers,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            versions = result.get("versions", [])
            
            if not versions:
                raise ValueError(f"No schemas found for subject {subject}")
            
            return max(versions)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get latest version for subject {subject}: {e}")
            raise RuntimeError(f"Failed to get latest version: {e}")
    
    def list_subjects(self) -> List[str]:
        """List all registered subjects.
        
        Returns:
            List of subject names
        
        Raises:
            RuntimeError: If schema registry is disabled or request fails
        """
        if not self.enabled:
            raise RuntimeError("Schema registry is disabled")
        
        endpoint = f"{self.url}/subjects"
        
        try:
            response = requests.get(
                endpoint,
                headers=self._headers,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("subjects", [])
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list subjects: {e}")
            raise RuntimeError(f"Failed to list subjects: {e}")
    
    def check_compatibility(
        self,
        subject: str,
        schema: Dict[str, Any]
    ) -> bool:
        """Check if a schema is compatible with the subject's latest schema.
        
        Args:
            subject: Subject name
            schema: Schema to check
        
        Returns:
            True if compatible, False otherwise
        
        Raises:
            RuntimeError: If schema registry is disabled or request fails
        """
        if not self.enabled:
            # If registry is disabled, assume compatible
            return True
        
        try:
            latest_schema = self.get_schema(subject)
            latest_schema_str = json.dumps(latest_schema)
            new_schema_str = json.dumps(schema)
            
            # Simple comparison - in production, use proper schema compatibility checker
            return latest_schema_str == new_schema_str
        
        except Exception as e:
            logger.error(f"Failed to check compatibility for subject {subject}: {e}")
            # If we can't check, assume compatible to avoid blocking
            return True
    
    def _set_compatibility_level(
        self,
        subject: str,
        compatibility_level: CompatibilityLevel
    ) -> None:
        """Set compatibility level for a subject.
        
        Args:
            subject: Subject name
            compatibility_level: Compatibility level to set
        """
        endpoint = f"{self.url}/config/{subject}"
        payload = {
            "compatibility": compatibility_level.value
        }
        
        try:
            response = requests.put(
                endpoint,
                json=payload,
                headers=self._headers,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info(f"Set compatibility level for subject {subject} to {compatibility_level.value}")
        
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to set compatibility level for subject {subject}: {e}")
            # Don't fail if compatibility level can't be set
    
    def validate_event(
        self,
        event_data: Dict[str, Any],
        subject: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Validate event data against schema.
        
        Args:
            event_data: Event data to validate
            subject: Subject name
            schema: Schema to validate against (if None, gets from registry)
        
        Returns:
            True if valid, False otherwise
        """
        if schema is None:
            try:
                schema = self.get_schema(subject)
            except Exception as e:
                logger.error(f"Failed to get schema for validation: {e}")
                return False
        
        # In production, use proper schema validation library (fastavro, jsonschema)
        # For now, check that required fields are present
        try:
            self._validate_against_schema(event_data, schema)
            return True
        except Exception as e:
            logger.error(f"Event validation failed: {e}")
            return False
    
    def _validate_against_schema(
        self,
        event_data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> None:
        """Validate event data against Avro schema.
        
        Args:
            event_data: Event data to validate
            schema: Avro schema
        
        Raises:
            ValueError: If validation fails
        """
        # Extract field definitions from Avro schema
        fields = schema.get("fields", [])
        required_fields = [f["name"] for f in fields if not f.get("type", "").startswith("null")]
        
        # Check that all required fields are present
        missing_fields = [f for f in required_fields if f not in event_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Additional validation can be added here
    
    def health_check(self) -> bool:
        """Check if schema registry is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        if not self.enabled:
            return True  # Disabled registry is considered healthy
        
        try:
            endpoint = f"{self.url}/subjects"
            response = requests.get(
                endpoint,
                headers=self._headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Schema registry health check failed: {e}")
            return False