"""MFA (Multi-Factor Authentication) resource module for Microsoft Graph.

This module provides access to Microsoft Graph MFA-related resources.
"""

import logging
from typing import Dict, List, Any, Optional
from utils.graph_client import GraphClient
from . import groups

logger = logging.getLogger(__name__)

async def get_mfa_status(graph_client: GraphClient, user_id: str) -> Optional[Dict[str, Any]]:
    """Get MFA status and methods for a specific user.
    
    Args:
        graph_client: GraphClient instance
        user_id: The unique identifier of the user
        
    Returns:
        A dictionary containing MFA status and methods information
    """
    try:
        client = graph_client.get_client()
        
        # Get user's authentication methods
        auth_methods_response = await client.users.by_user_id(user_id).authentication.methods.get()
        
        methods = []
        if auth_methods_response and auth_methods_response.value:
            for method in auth_methods_response.value:
                method_data = {
                    'id': getattr(method, 'id', None),
                    'type': getattr(method, 'odata_type', None),
                }
                
                # Add method-specific details
                if hasattr(method, 'phone_number'):
                    method_data['phoneNumber'] = getattr(method, 'phone_number', None)
                if hasattr(method, 'phone_type'):
                    method_data['phoneType'] = getattr(method, 'phone_type', None)
                if hasattr(method, 'email_address'):
                    method_data['emailAddress'] = getattr(method, 'email_address', None)
                    
                methods.append(method_data)
        
        # Determine MFA status based on available methods
        mfa_enabled = len([m for m in methods if m['type'] != '#microsoft.graph.passwordAuthenticationMethod']) > 0
        
        return {
            'userId': user_id,
            'mfaEnabled': mfa_enabled,
            'methodCount': len(methods),
            'methods': methods
        }
        
    except Exception as e:
        logger.error(f"Error fetching MFA status for user {user_id}: {str(e)}")
        raise

async def get_group_mfa_status(graph_client: GraphClient, group_id: str) -> List[Dict[str, Any]]:
    """Get MFA status for all members of a group.
    
    Args:
        graph_client: GraphClient instance
        group_id: The unique identifier of the group
        
    Returns:
        A list of dictionaries containing MFA status for each group member
    """
    try:
        # Get all group members
        members = await groups.get_group_members(graph_client, group_id)
        
        mfa_statuses = []
        for member in members:
            if member.get('type') == '#microsoft.graph.user':
                member_id = member.get('id')
                if member_id:
                    try:
                        mfa_status = await get_mfa_status(graph_client, member_id)
                        if mfa_status:
                            mfa_status.update({
                                'displayName': member.get('displayName'),
                                'userPrincipalName': member.get('userPrincipalName'),
                                'mail': member.get('mail')
                            })
                            mfa_statuses.append(mfa_status)
                    except Exception as e:
                        logger.warning(f"Could not get MFA status for user {member_id}: {str(e)}")
                        # Add a record indicating the error
                        mfa_statuses.append({
                            'userId': member_id,
                            'displayName': member.get('displayName'),
                            'userPrincipalName': member.get('userPrincipalName'),
                            'mail': member.get('mail'),
                            'mfaEnabled': None,
                            'error': str(e)
                        })
        
        return mfa_statuses
        
    except Exception as e:
        logger.error(f"Error fetching group MFA status for group {group_id}: {str(e)}")
        raise
