"""User resource module for Microsoft Graph.

This module provides comprehensive user lifecycle management including:
- User search and retrieval
- User creation, update, and deletion  
- Account enable/disable operations
- Manager relationship management
- Profile property updates (department, job title, etc.)
"""

import logging
from typing import Dict, List, Optional, Any

from msgraph.generated.users.users_request_builder import UsersRequestBuilder
from msgraph.generated.models.user import User
from msgraph.generated.models.password_profile import PasswordProfile
from msgraph.generated.models.directory_object import DirectoryObject
from kiota_abstractions.base_request_configuration import RequestConfiguration
from msgraph.generated.directory_roles.directory_roles_request_builder import DirectoryRolesRequestBuilder
from msgraph.generated.directory_roles.item.directory_role_item_request_builder import DirectoryRoleItemRequestBuilder
from msgraph.generated.directory_roles.item.members.members_request_builder import MembersRequestBuilder

from utils.graph_client import GraphClient

logger = logging.getLogger(__name__)

async def search_users(graph_client: GraphClient, query: str, limit: int = 10) -> List[Dict[str, str]]:
    """Search for users by name or email, with paging support."""
    try:
        client = graph_client.get_client()
        # Create query parameters for the search
        query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
            search=[
                f'(\\"displayName:{query}\\" OR \\"mail:{query}\\" OR \\"userPrincipalName:{query}\\" OR \\"givenName:{query}\\" OR \\"surName:{query}\\" OR \\"otherMails:{query}\\")'
            ],
            top=limit
        )
        # Create request configuration
        request_configuration = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )
        request_configuration.headers.add("ConsistencyLevel", "eventual")
        # Execute the search
        response = await client.users.get(request_configuration=request_configuration)
        users = []
        if response and response.value:
            users.extend(response.value)
        # Paging: fetch more if odata_next_link is present, but stop if we reach the limit
        while response is not None and getattr(response, 'odata_next_link', None) and len(users) < limit:
            response = await client.users.with_url(response.odata_next_link).get()
            if response and response.value:
                users.extend(response.value)
        # Format the response with all user fields
        formatted_users = []
        for user in users[:limit]:
            user_data = {
                'id': user.id,
                'displayName': user.display_name,
                'mail': user.mail,
                'userPrincipalName': user.user_principal_name,
                'givenName': user.given_name,
                'surname': user.surname,
                'jobTitle': user.job_title,
                'department': user.department,
                'officeLocation': user.office_location,
                'businessPhones': user.business_phones,
                'mobilePhone': user.mobile_phone,
                'accountEnabled': user.account_enabled,
                'usageLocation': user.usage_location,
                'companyName': user.company_name
            }
            formatted_users.append(user_data)
        return formatted_users
    except Exception as e:
        logger.error(f"Error searching users: {str(e)}")
        raise

async def get_user_by_id(graph_client: GraphClient, user_id: str) -> Optional[Dict[str, Any]]:
    """Get a user by their ID.
    
    Args:
        graph_client: GraphClient instance
        user_id: The unique identifier of the user.
        
    Returns:
        A dictionary containing the user's details if found, otherwise None.
    """
    try:
        client = graph_client.get_client()
        ms_user = await client.users.by_user_id(user_id).get()
        
        if ms_user:
            # Convert MS Graph User to our dictionary format
            user_data = {
                'id': ms_user.id,
                'displayName': ms_user.display_name,
                'mail': ms_user.mail,
                'userPrincipalName': ms_user.user_principal_name,
                'givenName': ms_user.given_name,
                'surname': ms_user.surname,
                'jobTitle': ms_user.job_title,
                'department': ms_user.department,
                'officeLocation': ms_user.office_location,
                'businessPhones': ms_user.business_phones,
                'mobilePhone': ms_user.mobile_phone,
                'accountEnabled': ms_user.account_enabled,
                'usageLocation': ms_user.usage_location,
                'companyName': ms_user.company_name,
                'preferredLanguage': ms_user.preferred_language,
                'createdDateTime': ms_user.created_date_time.isoformat() if ms_user.created_date_time else None
            }
            return user_data
        else:
            logger.warning(f"User with ID {user_id} not found.")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching user with ID {user_id}: {str(e)}")
        raise

async def update_user(graph_client: GraphClient, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing user's properties.
    
    Args:
        graph_client: GraphClient instance
        user_id: The unique identifier of the user
        user_data: Dictionary containing user properties to update:
          - displayName: Display name of the user
          - givenName: First name
          - surname: Last name  
          - jobTitle: Job title
          - department: Department
          - officeLocation: Office location
          - businessPhones: List of business phone numbers
          - mobilePhone: Mobile phone number
          - mail: Email address (if allowed in tenant)
          - userPrincipalName: UPN (if allowed)
          - accountEnabled: Enable/disable the user
          - usageLocation: Usage location (required for license assignment)
          - manager: Manager's user ID
          - companyName: Company name
          - preferredLanguage: Preferred language (e.g., "en-US")
          
    Returns:
        The updated user data
    """
    try:
        client = graph_client.get_client()
        
        # Create a user object with the provided update data
        user = User()
        
        # Set properties to update
        if 'displayName' in user_data:
            user.display_name = user_data['displayName']
        
        if 'givenName' in user_data:
            user.given_name = user_data['givenName']
        
        if 'surname' in user_data:
            user.surname = user_data['surname']
        
        if 'jobTitle' in user_data:
            user.job_title = user_data['jobTitle']
        
        if 'department' in user_data:
            user.department = user_data['department']
        
        if 'officeLocation' in user_data:
            user.office_location = user_data['officeLocation']
        
        if 'businessPhones' in user_data:
            user.business_phones = user_data['businessPhones']
        
        if 'mobilePhone' in user_data:
            user.mobile_phone = user_data['mobilePhone']
        
        if 'mail' in user_data:
            user.mail = user_data['mail']
        
        if 'userPrincipalName' in user_data:
            user.user_principal_name = user_data['userPrincipalName']
        
        if 'accountEnabled' in user_data:
            user.account_enabled = user_data['accountEnabled']
        
        if 'usageLocation' in user_data:
            user.usage_location = user_data['usageLocation']
        
        if 'companyName' in user_data:
            user.company_name = user_data['companyName']
        
        if 'preferredLanguage' in user_data:
            user.preferred_language = user_data['preferredLanguage']
        
        # Update the user
        await client.users.by_user_id(user_id).patch(user)
        
        # Handle manager assignment separately if provided
        if 'manager' in user_data:
            manager_id = user_data['manager']
            if manager_id:
                # Set manager reference
                manager_ref = DirectoryObject()
                manager_ref.id = manager_id
                await client.users.by_user_id(user_id).manager.ref.put(manager_ref)
            else:
                # Remove manager reference
                await client.users.by_user_id(user_id).manager.ref.delete()
        
        # Get the updated user to return
        updated_user = await get_user_by_id(graph_client, user_id)
        if not updated_user:
            raise Exception(f"Failed to retrieve updated user with ID {user_id}")
            
        return updated_user
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise

async def enable_user(graph_client: GraphClient, user_id: str) -> Dict[str, Any]:
    """Enable a user account.
    
    Args:
        graph_client: GraphClient instance
        user_id: The unique identifier of the user
        
    Returns:
        The updated user data
    """
    return await update_user(graph_client, user_id, {'accountEnabled': True})

async def disable_user(graph_client: GraphClient, user_id: str) -> Dict[str, Any]:
    """Disable a user account.
    
    Args:
        graph_client: GraphClient instance
        user_id: The unique identifier of the user
        
    Returns:
        The updated user data
    """
    return await update_user(graph_client, user_id, {'accountEnabled': False})

async def create_user(graph_client: GraphClient, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new user in Microsoft Graph.
    
    Args:
        graph_client: GraphClient instance
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
    try:
        client = graph_client.get_client()
        
        # Validate required fields
        required_fields = ['displayName', 'userPrincipalName', 'mailNickname', 'password']
        for field in required_fields:
            if field not in user_data:
                raise ValueError(f"{field} is required for creating a user")
        
        # Check if user already exists
        upn = user_data['userPrincipalName']
        try:
            existing_user = await client.users.by_user_id(upn).get()
            if existing_user:
                logger.info(f"User with UPN '{upn}' already exists")
                return {
                    'id': existing_user.id,
                    'displayName': existing_user.display_name,
                    'userPrincipalName': existing_user.user_principal_name,
                    'accountEnabled': existing_user.account_enabled,
                    'status': 'already_exists'
                }
        except Exception:
            # User doesn't exist, continue with creation
            pass
        
        # Create a user object
        user = User()
        
        # Set required properties
        user.display_name = user_data['displayName']
        user.user_principal_name = user_data['userPrincipalName']
        user.mail_nickname = user_data['mailNickname']
        user.account_enabled = user_data.get('accountEnabled', True)
        
        # Set password
        password_profile = PasswordProfile()
        password_profile.password = user_data['password']
        password_profile.force_change_password_next_sign_in = user_data.get('forceChangePasswordNextSignIn', True)
        user.password_profile = password_profile
        
        # Set optional properties
        if 'givenName' in user_data:
            user.given_name = user_data['givenName']
        
        if 'surname' in user_data:
            user.surname = user_data['surname']
        
        if 'jobTitle' in user_data:
            user.job_title = user_data['jobTitle']
        
        if 'department' in user_data:
            user.department = user_data['department']
        
        if 'usageLocation' in user_data:
            user.usage_location = user_data['usageLocation']
        
        if 'officeLocation' in user_data:
            user.office_location = user_data['officeLocation']
        
        if 'businessPhones' in user_data:
            user.business_phones = user_data['businessPhones']
        
        if 'mobilePhone' in user_data:
            user.mobile_phone = user_data['mobilePhone']
        
        # Create the user
        new_user = await client.users.post(user)
        
        if new_user:
            return {
                'id': new_user.id,
                'displayName': new_user.display_name,
                'userPrincipalName': new_user.user_principal_name,
                'mail': new_user.mail,
                'givenName': new_user.given_name,
                'surname': new_user.surname,
                'jobTitle': new_user.job_title,
                'department': new_user.department,
                'officeLocation': new_user.office_location,
                'accountEnabled': new_user.account_enabled,
                'createdDateTime': new_user.created_date_time.isoformat() if new_user.created_date_time else None
            }
        
        raise Exception("Failed to create user")
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise

async def delete_user(graph_client: GraphClient, user_id: str) -> bool:
    """Delete a user from Microsoft Graph.
    
    Args:
        graph_client: GraphClient instance
        user_id: The unique identifier of the user
        
    Returns:
        True if successful, raises an exception otherwise
    """
    try:
        client = graph_client.get_client()
        
        # Delete the user
        await client.users.by_user_id(user_id).delete()
        
        return True
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise

async def set_user_manager(graph_client: GraphClient, user_id: str, manager_id: str) -> Dict[str, Any]:
    """Set a user's manager.
    
    Args:
        graph_client: GraphClient instance
        user_id: The unique identifier of the user
        manager_id: The unique identifier of the manager
        
    Returns:
        Success message
    """
    try:
        client = graph_client.get_client()
        
        manager_ref = DirectoryObject()
        manager_ref.id = manager_id
        
        await client.users.by_user_id(user_id).manager.ref.put(manager_ref)
        
        return {"status": "success", "message": f"Manager {manager_id} set for user {user_id}"}
    except Exception as e:
        logger.error(f"Error setting manager for user {user_id}: {str(e)}")
        raise

async def remove_user_manager(graph_client: GraphClient, user_id: str) -> Dict[str, Any]:
    """Remove a user's manager.
    
    Args:
        graph_client: GraphClient instance
        user_id: The unique identifier of the user
        
    Returns:
        Success message
    """
    try:
        client = graph_client.get_client()
        
        await client.users.by_user_id(user_id).manager.ref.delete()
        
        return {"status": "success", "message": f"Manager removed for user {user_id}"}
    except Exception as e:
        logger.error(f"Error removing manager for user {user_id}: {str(e)}")
        raise

# Existing functions from original users.py continue below...

async def get_privileged_users(graph_client: GraphClient) -> List[Dict[str, Any]]:
    """Get all users who are members of privileged directory roles, with paging support for members."""
    try:
        client = graph_client.get_client()
        # Get all activated directory roles
        roles_response = await client.directory_roles.get()
        privileged_users = {}
        if roles_response and roles_response.value:
            for role in roles_response.value:
                # For each role, get its members (with paging)
                role_id = role.id
                role_name = getattr(role, 'display_name', None)
                if not role_id:
                    continue
                members_response = await client.directory_roles.by_directory_role_id(role_id).members.get()
                members = []
                if members_response and members_response.value:
                    members.extend(members_response.value)
                while members_response is not None and getattr(members_response, 'odata_next_link', None):
                    members_response = await client.directory_roles.by_directory_role_id(role_id).members.with_url(members_response.odata_next_link).get()
                    if members_response and members_response.value:
                        members.extend(members_response.value)
                for member in members:
                    # Only process user objects (type: #microsoft.graph.user)
                    if hasattr(member, 'odata_type') and member.odata_type == '#microsoft.graph.user':
                        user_id = getattr(member, 'id', None)
                        if not user_id:
                            continue
                        # Deduplicate by user_id
                        if user_id not in privileged_users:
                            privileged_users[user_id] = {
                                'id': user_id,
                                'displayName': getattr(member, 'display_name', None),
                                'mail': getattr(member, 'mail', None),
                                'userPrincipalName': getattr(member, 'user_principal_name', None),
                                'givenName': getattr(member, 'given_name', None),
                                'surname': getattr(member, 'surname', None),
                                'jobTitle': getattr(member, 'job_title', None),
                                'officeLocation': getattr(member, 'office_location', None),
                                'businessPhones': getattr(member, 'business_phones', None),
                                'mobilePhone': getattr(member, 'mobile_phone', None),
                                'roles': set()
                            }
                        # Add the role name to the user's roles set
                        privileged_users[user_id]['roles'].add(role_name)
        # Convert roles set to list for each user
        for user in privileged_users.values():
            user['roles'] = list(user['roles'])
        return list(privileged_users.values())
    except Exception as e:
        logger.error(f"Error fetching privileged users: {str(e)}")
        raise

async def get_user_groups(graph_client: GraphClient, user_id: str) -> List[Dict[str, Any]]:
    """Get all groups (including transitive memberships) for a user by user ID, with paging support."""
    try:
        client = graph_client.get_client()
        memberships_response = await client.users.by_user_id(user_id).transitive_member_of.get()
        memberships = []
        if memberships_response and memberships_response.value:
            memberships.extend(memberships_response.value)
        # Paging for memberships
        while memberships_response is not None and getattr(memberships_response, 'odata_next_link', None):
            memberships_response = await client.users.by_user_id(user_id).transitive_member_of.with_url(memberships_response.odata_next_link).get()
            if memberships_response and memberships_response.value:
                memberships.extend(memberships_response.value)
        # For each membership, fetch group details if it is a group
        groups_list = []
        for membership in memberships:
            if hasattr(membership, 'odata_type') and membership.odata_type == '#microsoft.graph.group':
                group_id = getattr(membership, 'id', None)
                if not group_id:
                    continue
                group = await client.groups.by_group_id(group_id).get()
                if group:
                    group_data = {
                        'id': group.id,
                        'displayName': getattr(group, 'display_name', None),
                        'mail': getattr(group, 'mail', None),
                        'groupTypes': getattr(group, 'group_types', None),
                        'description': getattr(group, 'description', None)
                    }
                    groups_list.append(group_data)
        return groups_list
    except Exception as e:
        logger.error(f"Error fetching groups for user {user_id}: {str(e)}")
        raise

async def get_user_roles(graph_client: GraphClient, user_id: str) -> List[Dict[str, Any]]:
    """Get all directory roles assigned to a user by user ID, with paging support."""
    try:
        client = graph_client.get_client()
        memberof_response = await client.users.by_user_id(user_id).member_of.get()
        memberships = []
        if memberof_response and memberof_response.value:
            memberships.extend(memberof_response.value)
        # Paging for memberOf
        while memberof_response is not None and getattr(memberof_response, 'odata_next_link', None):
            memberof_response = await client.users.by_user_id(user_id).member_of.with_url(memberof_response.odata_next_link).get()
            if memberof_response and memberof_response.value:
                memberships.extend(memberof_response.value)
        # For each membership, filter for directoryRole objects
        roles_list = []
        for membership in memberships:
            if hasattr(membership, 'odata_type') and membership.odata_type == '#microsoft.graph.directoryRole':
                role_id = getattr(membership, 'id', None)
                if not role_id:
                    continue
                # Optionally fetch more details if needed
                role = await client.directory_roles.by_directory_role_id(role_id).get()
                if role:
                    role_data = {
                        'id': role.id,
                        'displayName': getattr(role, 'display_name', None),
                        'description': getattr(role, 'description', None),
                        'roleTemplateId': getattr(role, 'role_template_id', None)
                    }
                    roles_list.append(role_data)
        return roles_list
    except Exception as e:
        logger.error(f"Error fetching roles for user {user_id}: {str(e)}")
        raise
