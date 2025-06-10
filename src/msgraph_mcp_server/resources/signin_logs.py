"""Sign-in logs resource module for Microsoft Graph.

This module provides access to Microsoft Graph sign-in log resources.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from msgraph.generated.audit_logs.sign_ins.sign_ins_request_builder import SignInsRequestBuilder
from utils.graph_client import GraphClient

logger = logging.getLogger(__name__)

async def get_user_sign_in_logs(graph_client: GraphClient, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """Get sign-in logs for a specific user within the last N days.
    
    Args:
        graph_client: GraphClient instance
        user_id: The unique identifier (ID) of the user
        days: The number of past days to retrieve logs for (default: 7)
        
    Returns:
        A list of dictionaries, each representing a sign-in log event
    """
    try:
        client = graph_client.get_client()
        
        # Calculate the date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days)
        date_filter = date_threshold.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        # Create filter for user and date
        filter_query = f"userId eq '{user_id}' and createdDateTime ge {date_filter}"
        
        # Set up query parameters
        query_params = SignInsRequestBuilder.SignInsRequestBuilderGetQueryParameters(
            filter=filter_query,
            top=1000  # Maximum allowed by Graph API
        )
        
        request_configuration = SignInsRequestBuilder.SignInsRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )
        
        # Execute the request
        response = await client.audit_logs.sign_ins.get(request_configuration=request_configuration)
        
        sign_ins = []
        if response and response.value:
            sign_ins.extend(response.value)
        
        # Handle paging if there are more results
        while response is not None and getattr(response, 'odata_next_link', None):
            response = await client.audit_logs.sign_ins.with_url(response.odata_next_link).get()
            if response and response.value:
                sign_ins.extend(response.value)
        
        # Format the results
        formatted_logs = []
        for sign_in in sign_ins:
            log_data = {
                'id': getattr(sign_in, 'id', None),
                'createdDateTime': getattr(sign_in, 'created_date_time', None).isoformat() if getattr(sign_in, 'created_date_time', None) else None,
                'userDisplayName': getattr(sign_in, 'user_display_name', None),
                'userPrincipalName': getattr(sign_in, 'user_principal_name', None),
                'userId': getattr(sign_in, 'user_id', None),
                'appDisplayName': getattr(sign_in, 'app_display_name', None),
                'appId': getattr(sign_in, 'app_id', None),
                'ipAddress': getattr(sign_in, 'ip_address', None),
                'clientAppUsed': getattr(sign_in, 'client_app_used', None),
                'conditionalAccessStatus': getattr(sign_in, 'conditional_access_status', None),
                'isInteractive': getattr(sign_in, 'is_interactive', None),
                'riskDetail': getattr(sign_in, 'risk_detail', None),
                'riskLevelAggregated': getattr(sign_in, 'risk_level_aggregated', None),
                'riskLevelDuringSignIn': getattr(sign_in, 'risk_level_during_sign_in', None),
                'riskState': getattr(sign_in, 'risk_state', None),
                'deviceDetail': {
                    'deviceId': getattr(getattr(sign_in, 'device_detail', None), 'device_id', None),
                    'displayName': getattr(getattr(sign_in, 'device_detail', None), 'display_name', None),
                    'operatingSystem': getattr(getattr(sign_in, 'device_detail', None), 'operating_system', None),
                    'browser': getattr(getattr(sign_in, 'device_detail', None), 'browser', None),
                    'isCompliant': getattr(getattr(sign_in, 'device_detail', None), 'is_compliant', None),
                    'isManaged': getattr(getattr(sign_in, 'device_detail', None), 'is_managed', None),
                    'trustType': getattr(getattr(sign_in, 'device_detail', None), 'trust_type', None)
                } if getattr(sign_in, 'device_detail', None) else None,
                'location': {
                    'city': getattr(getattr(sign_in, 'location', None), 'city', None),
                    'state': getattr(getattr(sign_in, 'location', None), 'state', None),
                    'countryOrRegion': getattr(getattr(sign_in, 'location', None), 'country_or_region', None),
                    'geoCoordinates': {
                        'altitude': getattr(getattr(getattr(sign_in, 'location', None), 'geo_coordinates', None), 'altitude', None),
                        'latitude': getattr(getattr(getattr(sign_in, 'location', None), 'geo_coordinates', None), 'latitude', None),
                        'longitude': getattr(getattr(getattr(sign_in, 'location', None), 'geo_coordinates', None), 'longitude', None)
                    } if getattr(getattr(sign_in, 'location', None), 'geo_coordinates', None) else None
                } if getattr(sign_in, 'location', None) else None,
                'status': {
                    'errorCode': getattr(getattr(sign_in, 'status', None), 'error_code', None),
                    'failureReason': getattr(getattr(sign_in, 'status', None), 'failure_reason', None),
                    'additionalDetails': getattr(getattr(sign_in, 'status', None), 'additional_details', None)
                } if getattr(sign_in, 'status', None) else None
            }
            formatted_logs.append(log_data)
        
        return formatted_logs
        
    except Exception as e:
        logger.error(f"Error fetching sign-in logs for user {user_id}: {str(e)}")
        raise
