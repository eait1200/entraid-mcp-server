"""Microsoft Graph authentication module.

This module provides authentication functionality for the Microsoft Graph API
using Azure Identity credentials.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential, CertificateCredential
from msgraph import GraphServiceClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to load environment variables from multiple possible locations
env_paths = [
    # Project root config directory
    Path(__file__).parent.parent.parent / "config" / ".env",
    # Current working directory config
    Path.cwd() / "config" / ".env",
    # User's home directory
    Path.home() / ".entraid" / ".env",
    # System-wide config
    Path("/etc/entraid/.env")
]

env_loaded = False
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from {env_path}")
        env_loaded = True
        break

if not env_loaded:
    logger.warning("No .env file found in any of the expected locations")

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

class GraphAuthManager:
    """Authentication manager for Microsoft Graph API."""
    
    def __init__(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        certificate_path: Optional[str] = None,
        certificate_pwd: Optional[str] = None,
        scopes: Optional[List[str]] = None
    ):
        """Initialize the GraphAuthManager.
        
        Args:
            tenant_id: Azure tenant ID
            client_id: Azure application client ID
            client_secret: Azure application client secret
            certificate_path: Path to certificate file
            certificate_pwd: Certificate password
            scopes: List of Microsoft Graph API scopes to request
        """
        # Try to get credentials from parameters first, then environment
        self.tenant_id = tenant_id or os.environ.get("TENANT_ID")
        self.client_id = client_id or os.environ.get("CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("CLIENT_SECRET")
        self.certificate_path = certificate_path or os.environ.get("CERTIFICATE_PATH")
        self.certificate_pwd = certificate_pwd or os.environ.get("CERTIFICATE_PWD")
        self.scopes = scopes or ["https://graph.microsoft.com/.default"]
        self._graph_client = None
        
        # Log the state of credentials (without exposing sensitive data)
        logger.info("Initializing GraphAuthManager with credentials:")
        logger.info(f"TENANT_ID: {'Set' if self.tenant_id else 'Not set'}")
        logger.info(f"CLIENT_ID: {'Set' if self.client_id else 'Not set'}")
        logger.info(f"CLIENT_SECRET: {'Set' if self.client_secret else 'Not set'}")
        
        # Validate credentials
        self._validate_credentials()
    
    def _validate_credentials(self):
        """Validate that all required credentials are present."""
        missing = []
        if not self.tenant_id:
            missing.append("tenant_id")
        if not self.client_id:
            missing.append("client_id")
        if not self.client_secret:
            missing.append("client_secret")
            
        if missing:
            error_msg = f"Missing required credentials: {', '.join(missing)}"
            logger.error(error_msg)
            raise AuthenticationError(error_msg)
    
    def get_graph_client(self) -> GraphServiceClient:
        """Get a Microsoft Graph client.
        
        Returns:
            GraphServiceClient: Authenticated Microsoft Graph client
            
        Raises:
            AuthenticationError: If authentication fails or required parameters are missing
        """
        if self._graph_client:
            return self._graph_client
            
        try:
            credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            self._graph_client = GraphServiceClient(
                credentials=credential,
                scopes=self.scopes
            )
            logger.info("Successfully created Graph client")
            return self._graph_client
            
        except Exception as e:
            error_msg = f"Failed to create Graph client: {str(e)}"
            logger.error(error_msg)
            raise AuthenticationError(error_msg)
