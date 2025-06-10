"""Microsoft Graph MCP Server (Enhanced).

This module provides the main FastMCP server implementation for
interacting with Microsoft Graph services with comprehensive
user lifecycle management capabilities.
"""

import logging
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP, Context

from auth.graph_auth import GraphAuthManager, AuthenticationError
from utils.graph_client import GraphClient
from utils.password_generator import generate_secure_password
from resources import users, signin_logs, mfa, groups

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create an MCP server
mcp = FastMCP("Enhanced EntraID MCP Server")

# Initialize Graph client
try:
    auth_manager = GraphAuthManager()
    graph_client = GraphClient(auth_manager)
    logger.info("Successfully initialized Graph client")
except AuthenticationError as e:
    logger.error(f"Failed to initialize Graph client: {str(e)}")
    raise

# =============================================================================
# ENHANCED USER MANAGEMENT TOOLS
# =============================================================================

@mcp.tool()
async def search_users(query: str, ctx: Context, limit: int = 10) -> List[Dict[str, str]]:
    """Search for users by name or email.
    
    Args:
        query: Search query (name or email)
        ctx: Context object
        limit: Maximum number of results to return (default: 10)
    """
    await ctx.info(f"Searching for users matching '{query}'...")
    
    try:
        results = await users.search_users(graph_client, query, limit)
        await ctx.report_progress(progress=100, total=100)
        return results
    except AuthenticationError as e:
        error_msg = f"Authentication error: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error searching users: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def get_user_by_id(user_id: str, ctx: Context) -> Optional[Dict[str, Any]]:
    """Get a specific user by their ID.
    
    Args:
        user_id: The unique identifier (ID) of the user.
        ctx: Context object
        
    Returns:
        A dictionary containing the user's details if found, otherwise None.
    """
    await ctx.info(f"Fetching user with ID: {user_id}...")
    
    try:
        result = await users.get_user_by_id(graph_client, user_id)
        await ctx.report_progress(progress=100, total=100)
        if not result:
            await ctx.warning(f"User with ID {user_id} not found.")
        return result
    except AuthenticationError as e:
        error_msg = f"Authentication error: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error fetching user {user_id}: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def update_user(user_id: str, ctx: Context, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing user's properties.
    
    Args:
        user_id: The unique identifier of the user
        ctx: Context object
        user_data: Dictionary containing user properties to update:
          - displayName: Display name of the user
          - givenName: First name
          - surname: Last name  
          - jobTitle: Job title
          - department: Department
          - officeLocation: Office location
          - businessPhones: List of business phone numbers
          - mobilePhone: Mobile phone number
          - accountEnabled: Enable/disable the user
          - usageLocation: Usage location (required for license assignment)
          - manager: Manager's user ID
          - companyName: Company name
          - preferredLanguage: Preferred language (e.g., "en-US")
          
    Returns:
        The updated user data
    """
    await ctx.info(f"Updating user {user_id}...")
    
    try:
        result = await users.update_user(graph_client, user_id, user_data)
        await ctx.report_progress(progress=100, total=100)
        await ctx.info(f"Successfully updated user {user_id}")
        return result
    except Exception as e:
        error_msg = f"Error updating user {user_id}: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def enable_user(user_id: str, ctx: Context) -> Dict[str, Any]:
    """Enable a user account.
    
    Args:
        user_id: The unique identifier of the user
        ctx: Context object
        
    Returns:
        The updated user data
    """
    await ctx.info(f"Enabling user {user_id}...")
    
    try:
        result = await users.enable_user(graph_client, user_id)
        await ctx.report_progress(progress=100, total=100)
        await ctx.info(f"Successfully enabled user {user_id}")
        return result
    except Exception as e:
        error_msg = f"Error enabling user {user_id}: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def disable_user(user_id: str, ctx: Context) -> Dict[str, Any]:
    """Disable a user account.
    
    Args:
        user_id: The unique identifier of the user
        ctx: Context object
        
    Returns:
        The updated user data
    """
    await ctx.info(f"Disabling user {user_id}...")
    
    try:
        result = await users.disable_user(graph_client, user_id)
        await ctx.report_progress(progress=100, total=100)
        await ctx.info(f"Successfully disabled user {user_id}")
        return result
    except Exception as e:
        error_msg = f"Error disabling user {user_id}: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def create_user(ctx: Context, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new user.
    
    Args:
        ctx: Context object
        user_data: Dictionary containing user properties:
          - displayName: Display name of the user (required)
          - userPrincipalName: UPN like user@domain.com (required)
          - mailNickname: Mail nickname (required)
          - password: Initial password (required)
          - accountEnabled: Whether account is enabled (default: True)
          - forceChangePasswordNextSignIn: Force password change (default: True)
          - givenName: First name (optional)
          - surname: Last name (optional)
          - jobTitle: Job title (optional)
          - department: Department (optional)
          - usageLocation: Usage location like "US" (optional but recommended)
          - officeLocation: Office location (optional)
          - businessPhones: List of business phone numbers (optional)
          - mobilePhone: Mobile phone number (optional)
        
    Returns:
        The created user data
    """
    await ctx.info(f"Creating user '{user_data.get('displayName', 'unnamed')}'...")
    
    try:
        # Validate required fields
        required_fields = ['displayName', 'userPrincipalName', 'mailNickname', 'password']
        for field in required_fields:
            if not user_data.get(field):
                raise ValueError(f"{field} is required for creating a user")
        
        result = await users.create_user(graph_client, user_data)
        await ctx.report_progress(progress=100, total=100)
        
        if result.get('status') == 'already_exists':
            await ctx.info(f"User with UPN '{result.get('userPrincipalName')}' already exists (ID: {result.get('id')})")
        else:
            await ctx.info(f"Successfully created user with ID: {result.get('id')}")
            
        return result
    except Exception as e:
        error_msg = f"Error creating user: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def delete_user(user_id: str, ctx: Context) -> Dict[str, Any]:
    """Delete a user.
    
    Args:
        user_id: The unique identifier of the user
        ctx: Context object
        
    Returns:
        A dictionary with the operation result
    """
    await ctx.info(f"Deleting user {user_id}...")
    
    try:
        await users.delete_user(graph_client, user_id)
        await ctx.report_progress(progress=100, total=100)
        await ctx.info(f"Successfully deleted user {user_id}")
        return {"status": "success", "message": f"User {user_id} was deleted successfully"}
    except Exception as e:
        error_msg = f"Error deleting user {user_id}: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def set_user_manager(user_id: str, manager_id: str, ctx: Context) -> Dict[str, Any]:
    """Set a user's manager.
    
    Args:
        user_id: The unique identifier of the user
        manager_id: The unique identifier of the manager
        ctx: Context object
        
    Returns:
        A dictionary with the operation result
    """
    await ctx.info(f"Setting manager {manager_id} for user {user_id}...")
    
    try:
        result = await users.set_user_manager(graph_client, user_id, manager_id)
        await ctx.report_progress(progress=100, total=100)
        await ctx.info(f"Successfully set manager for user {user_id}")
        return result
    except Exception as e:
        error_msg = f"Error setting manager for user {user_id}: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def remove_user_manager(user_id: str, ctx: Context) -> Dict[str, Any]:
    """Remove a user's manager.
    
    Args:
        user_id: The unique identifier of the user
        ctx: Context object
        
    Returns:
        A dictionary with the operation result
    """
    await ctx.info(f"Removing manager for user {user_id}...")
    
    try:
        result = await users.remove_user_manager(graph_client, user_id)
        await ctx.report_progress(progress=100, total=100)
        await ctx.info(f"Successfully removed manager for user {user_id}")
        return result
    except Exception as e:
        error_msg = f"Error removing manager for user {user_id}: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

# =============================================================================
# EXISTING USER TOOLS (ENHANCED)
# =============================================================================

@mcp.tool()
async def get_privileged_users(ctx: Context) -> List[Dict[str, Any]]:
    """Get all users who are members of privileged directory roles."""
    await ctx.info("Fetching privileged users...")
    try:
        privileged_users_list = await users.get_privileged_users(graph_client)
        await ctx.report_progress(progress=100, total=100)
        return privileged_users_list
    except Exception as e:
        await ctx.error(f"Error fetching privileged users: {str(e)}")
        raise

@mcp.tool()
async def get_user_groups(user_id: str, ctx: Context) -> List[Dict[str, Any]]:
    """Get all groups (including transitive memberships) for a user by user ID."""
    await ctx.info(f"Fetching all groups for user {user_id}...")
    try:
        results = await users.get_user_groups(graph_client, user_id)
        await ctx.report_progress(progress=100, total=100)
        return results
    except Exception as e:
        error_msg = f"Error fetching groups for user {user_id}: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def get_user_roles(user_id: str, ctx: Context) -> List[Dict[str, Any]]:
    """Get all directory roles assigned to a user by user ID."""
    await ctx.info(f"Fetching all directory roles for user {user_id}...")
    try:
        results = await users.get_user_roles(graph_client, user_id)
        await ctx.report_progress(progress=100, total=100)
        return results
    except Exception as e:
        error_msg = f"Error fetching roles for user {user_id}: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

# =============================================================================
# GROUP MANAGEMENT TOOLS
# =============================================================================

@mcp.tool()
async def get_all_groups(ctx: Context, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all groups (up to the specified limit, with paging)."""
    await ctx.info(f"Fetching up to {limit} groups...")
    try:
        results = await groups.get_all_groups(graph_client, limit)
        await ctx.report_progress(progress=100, total=100)
        return results
    except Exception as e:
        error_msg = f"Error fetching all groups: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def get_group_by_id(group_id: str, ctx: Context) -> Optional[Dict[str, Any]]:
    """Get a specific group by its ID."""
    await ctx.info(f"Fetching group with ID: {group_id}...")
    try:
        result = await groups.get_group_by_id(graph_client, group_id)
        await ctx.report_progress(progress=100, total=100)
        if not result:
            await ctx.warning(f"Group with ID {group_id} not found.")
        return result
    except Exception as e:
        error_msg = f"Error fetching group {group_id}: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def search_groups_by_name(name: str, ctx: Context, limit: int = 50) -> List[Dict[str, Any]]:
    """Search for groups by display name (case-insensitive, partial match, with paging)."""
    await ctx.info(f"Searching for groups with name matching '{name}'...")
    try:
        results = await groups.search_groups_by_name(graph_client, name, limit)
        await ctx.report_progress(progress=100, total=100)
        return results
    except Exception as e:
        error_msg = f"Error searching groups by name: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def get_group_members(group_id: str, ctx: Context, limit: int = 100) -> List[Dict[str, Any]]:
    """Get members of a group by group ID (up to the specified limit, with paging)."""
    await ctx.info(f"Fetching up to {limit} members for group {group_id}...")
    try:
        results = await groups.get_group_members(graph_client, group_id, limit)
        await ctx.report_progress(progress=100, total=100)
        return results
    except Exception as e:
        error_msg = f"Error fetching group members for group {group_id}: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

# =============================================================================
# SECURITY & COMPLIANCE TOOLS
# =============================================================================

@mcp.tool()
async def get_user_sign_ins(user_id: str, ctx: Context, days: int = 7) -> List[Dict[str, Any]]:
    """Get sign-in logs for a specific user within the last N days.

    Requires AuditLog.Read.All permission.
    
    Args:
        user_id: The unique identifier (ID) of the user.
        ctx: Context object
        days: The number of past days to retrieve logs for (default: 7).
        
    Returns:
        A list of dictionaries, each representing a sign-in log event.
    """
    await ctx.info(f"Fetching sign-in logs for user {user_id} for the last {days} days...")
    
    try:
        logs = await signin_logs.get_user_sign_in_logs(graph_client, user_id, days)
        await ctx.report_progress(progress=100, total=100)
        if not logs:
            await ctx.info(f"No sign-in logs found for user {user_id} in the last {days} days.")
        return logs
    except AuthenticationError as e:
        error_msg = f"Authentication error: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error fetching sign-in logs for {user_id}: {str(e)}"
        # Check for permission errors specifically
        if "Authorization_RequestDenied" in str(e):
             error_msg += " (Ensure the application has AuditLog.Read.All permission)"
             await ctx.error(error_msg)
        else:
            await ctx.error(error_msg)
        logger.error(error_msg)
        raise

@mcp.tool()
async def get_user_mfa_status(user_id: str, ctx: Context) -> Optional[Dict[str, Any]]:
    """Get MFA status and methods for a specific user.
    
    Args:
        user_id: The unique identifier of the user.
        ctx: Context object
        
    Returns:
        A dictionary containing MFA status and methods information.
    """
    await ctx.info(f"Fetching MFA status for user {user_id}...")
    
    try:
        result = await mfa.get_mfa_status(graph_client, user_id)
        await ctx.report_progress(progress=100, total=100)
        if not result:
            await ctx.warning(f"No MFA data found for user {user_id}")
        return result
    except AuthenticationError as e:
        error_msg = f"Authentication error: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error fetching MFA status for {user_id}: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

@mcp.tool()
async def get_group_mfa_status(group_id: str, ctx: Context) -> List[Dict[str, Any]]:
    """Get MFA status for all members of a group.
    
    Args:
        group_id: The unique identifier of the group.
        ctx: Context object
        
    Returns:
        A list of dictionaries containing MFA status for each group member.
    """
    await ctx.info(f"Fetching MFA status for group {group_id}...")
    
    try:
        results = await mfa.get_group_mfa_status(graph_client, group_id)
        await ctx.report_progress(progress=100, total=100)
        if not results:
            await ctx.warning(f"No MFA data found for group {group_id}")
        return results
    except AuthenticationError as e:
        error_msg = f"Authentication error: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Error fetching group MFA status for {group_id}: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

# =============================================================================
# RESOURCE ENDPOINT
# =============================================================================

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! Welcome to the Enhanced EntraID MCP Server!"

# Start the server
if __name__ == "__main__":
    mcp.run()
