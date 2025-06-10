"""Groups resource module for Microsoft Graph.

This module provides access to Microsoft Graph group resources.
"""

import logging
from typing import Dict, List, Any, Optional
from msgraph.generated.groups.groups_request_builder import GroupsRequestBuilder
from msgraph.generated.models.group import Group
from msgraph.generated.models.directory_object import DirectoryObject
from utils.graph_client import GraphClient

logger = logging.getLogger(__name__)

async def get_all_groups(graph_client: GraphClient, limit: int = 100) -> List[Dict[str, Any]]:
    """Get all groups (up to the specified limit, with paging)."""
    try:
        client = graph_client.get_client()
        query_params = GroupsRequestBuilder.GroupsRequestBuilderGetQueryParameters(top=limit)
        request_configuration = GroupsRequestBuilder.GroupsRequestBuilderGetRequestConfiguration(query_parameters=query_params)
        response = await client.groups.get(request_configuration=request_configuration)
        groups = []
        if response and response.value:
            groups.extend(response.value)
        # Paging: fetch more if odata_next_link is present
        while response is not None and getattr(response, 'odata_next_link', None):
            response = await client.groups.with_url(response.odata_next_link).get()
            if response and response.value:
                groups.extend(response.value)
        # Format output
        formatted_groups = []
        for group in groups[:limit]:
            group_data = {
                'id': group.id,
                'displayName': group.display_name,
                'mail': group.mail,
                'mailNickname': group.mail_nickname,
                'description': group.description,
                'groupTypes': group.group_types,
                'securityEnabled': group.security_enabled,
                'mailEnabled': group.mail_enabled,
                'createdDateTime': group.created_date_time.isoformat() if group.created_date_time else None
            }
            formatted_groups.append(group_data)
        return formatted_groups
    except Exception as e:
        logger.error(f"Error fetching all groups: {str(e)}")
        raise

async def get_group_by_id(graph_client: GraphClient, group_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific group by ID."""
    try:
        client = graph_client.get_client()
        group = await client.groups.by_group_id(group_id).get()
        
        if group:
            group_data = {
                'id': group.id,
                'displayName': group.display_name,
                'mail': group.mail,
                'mailNickname': group.mail_nickname,
                'description': group.description,
                'groupTypes': group.group_types,
                'securityEnabled': group.security_enabled,
                'mailEnabled': group.mail_enabled,
                'visibility': group.visibility,
                'createdDateTime': group.created_date_time.isoformat() if group.created_date_time else None
            }
            return group_data
        return None
    except Exception as e:
        logger.error(f"Error fetching group {group_id}: {str(e)}")
        raise

async def search_groups_by_name(graph_client: GraphClient, name: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search for groups by display name (case-insensitive, partial match, with paging)."""
    try:
        client = graph_client.get_client()
        filter_query = f"startswith(displayName,'{name}')"
        query_params = GroupsRequestBuilder.GroupsRequestBuilderGetQueryParameters(
            filter=filter_query, top=limit
        )
        request_configuration = GroupsRequestBuilder.GroupsRequestBuilderGetRequestConfiguration(query_parameters=query_params)
        response = await client.groups.get(request_configuration=request_configuration)
        groups = []
        if response and response.value:
            groups.extend(response.value)
        # Paging
        while response is not None and getattr(response, 'odata_next_link', None):
            response = await client.groups.with_url(response.odata_next_link).get()
            if response and response.value:
                groups.extend(response.value)
        formatted_groups = []
        for group in groups[:limit]:
            group_data = {
                'id': group.id,
                'displayName': group.display_name,
                'mail': group.mail,
                'mailNickname': group.mail_nickname,
                'description': group.description,
                'groupTypes': group.group_types,
                'securityEnabled': group.security_enabled,
                'mailEnabled': group.mail_enabled,
                'createdDateTime': group.created_date_time.isoformat() if group.created_date_time else None
            }
            formatted_groups.append(group_data)
        return formatted_groups
    except Exception as e:
        logger.error(f"Error searching groups by name: {str(e)}")
        raise

async def get_group_members(graph_client: GraphClient, group_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get members of a group by group ID (up to the specified limit, with paging)."""
    try:
        client = graph_client.get_client()
        members_response = await client.groups.by_group_id(group_id).members.get()
        members = []
        if members_response and members_response.value:
            members.extend(members_response.value)
        # Paging
        while members_response is not None and getattr(members_response, 'odata_next_link', None):
            members_response = await client.groups.by_group_id(group_id).members.with_url(members_response.odata_next_link).get()
            if members_response and members_response.value:
                members.extend(members_response.value)
        formatted_members = []
        for member in members[:limit]:
            member_data = {
                'id': getattr(member, 'id', None),
                'displayName': getattr(member, 'display_name', None),
                'mail': getattr(member, 'mail', None),
                'userPrincipalName': getattr(member, 'user_principal_name', None),
                'givenName': getattr(member, 'given_name', None),
                'surname': getattr(member, 'surname', None),
                'jobTitle': getattr(member, 'job_title', None),
                'officeLocation': getattr(member, 'office_location', None),
                'businessPhones': getattr(member, 'business_phones', None),
                'mobilePhone': getattr(member, 'mobile_phone', None),
                'type': getattr(member, 'odata_type', None)
            }
            formatted_members.append(member_data)
        return formatted_members
    except Exception as e:
        logger.error(f"Error fetching group members for group {group_id}: {str(e)}")
        raise
