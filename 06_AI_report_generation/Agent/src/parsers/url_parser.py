"""Grafana dashboard URL parser"""

from urllib.parse import urlparse, parse_qs
from datetime import datetime
from dataclasses import dataclass
from typing import Dict


@dataclass
class GrafanaDashboardContext:
    """Parsed Grafana dashboard URL context"""
    base_url: str
    dashboard_uid: str
    org_id: str
    time_from: datetime
    time_to: datetime
    timezone: str
    variables: Dict[str, str]
    raw_url: str


class GrafanaURLParser:
    """Parse Grafana dashboard URL to extract all context"""
    
    def parse(self, dashboard_url: str) -> GrafanaDashboardContext:
        """
        Parse Grafana dashboard URL
        
        Args:
            dashboard_url: Full Grafana dashboard URL with parameters
            
        Returns:
            GrafanaDashboardContext with all extracted information
        """
        parsed = urlparse(dashboard_url)
        params = parse_qs(parsed.query)
        
        # Extract base URL
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Extract dashboard UID from path: /d/{uid}/{slug} or /d/{uid}
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] == 'd':
            dashboard_uid = path_parts[1]
        else:
            raise ValueError(f"Invalid dashboard URL format: {dashboard_url}")
        
        # Extract time range
        time_from = self._parse_time(params.get('from', [''])[0])
        time_to = self._parse_time(params.get('to', [''])[0])
        
        # Extract organization ID
        org_id = params.get('orgId', ['1'])[0]
        
        # Extract timezone
        timezone = params.get('timezone', ['browser'])[0]
        
        # Extract all variables (parameters starting with 'var-')
        variables = {
            key.replace('var-', ''): value[0]
            for key, value in params.items()
            if key.startswith('var-')
        }
        
        return GrafanaDashboardContext(
            base_url=base_url,
            dashboard_uid=dashboard_uid,
            org_id=org_id,
            time_from=time_from,
            time_to=time_to,
            timezone=timezone,
            variables=variables,
            raw_url=dashboard_url
        )
    
    def _parse_time(self, time_str: str) -> datetime:
        """Parse Grafana time format to datetime"""
        if not time_str:
            raise ValueError("Time parameter is missing")
        
        # Handle ISO format: 2025-11-17T21:54:08.137Z
        try:
            if time_str.endswith('Z'):
                time_str = time_str[:-1] + '+00:00'
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except ValueError as e:
            raise ValueError(f"Unsupported time format: {time_str}") from e
    
    def get_time_range_description(self, context: GrafanaDashboardContext) -> str:
        """Generate human-readable time range description"""
        duration = context.time_to - context.time_from
        
        hours = duration.total_seconds() / 3600
        minutes = (duration.total_seconds() % 3600) / 60
        
        if hours >= 1:
            return f"{hours:.1f} hours ({context.time_from.strftime('%Y-%m-%d %H:%M')} to {context.time_to.strftime('%Y-%m-%d %H:%M')})"
        else:
            return f"{minutes:.0f} minutes ({context.time_from.strftime('%H:%M:%S')} to {context.time_to.strftime('%H:%M:%S')})"

