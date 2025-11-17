"""Grafana API client"""

import os
import json
import requests
from typing import Dict, List, Any
from ..parsers.url_parser import GrafanaDashboardContext


class GrafanaClient:
    """Grafana API client with service account token authentication"""
    
    def __init__(self, context: GrafanaDashboardContext):
        """
        Initialize Grafana client
        
        Args:
            context: Parsed dashboard context from URL
        """
        self._base_url = context.base_url
        self._dashboard_uid = context.dashboard_uid
        self._org_id = context.org_id
        self._time_from = context.time_from
        self._time_to = context.time_to
        self._variables = context.variables
        
        # Read token from environment
        token = os.getenv('SERVICE_ACCOUNT_TOKEN')
        if not token:
            raise ValueError("SERVICE_ACCOUNT_TOKEN not found in environment")
        
        self._headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        self._session = requests.Session()
        self._session.headers.update(self._headers)
    
    def get_dashboard(self) -> Dict[str, Any]:
        """
        Get dashboard by UID extracted from URL
        
        Returns:
            Dashboard JSON with panels and configuration
        """
        url = f"{self._base_url}/api/dashboards/uid/{self._dashboard_uid}"
        response = self._session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_panel_data(
        self, 
        panel_id: int, 
        datasource_uid: str,
        queries: List[Dict]
    ) -> Dict[str, Any]:
        """
        Query panel data using datasource
        
        Args:
            panel_id: Panel ID from dashboard
            datasource_uid: Datasource UID
            queries: Panel queries from dashboard JSON
            
        Returns:
            Query results with time series data
        """
        url = f"{self._base_url}/api/ds/query"
        
        # Convert datetime to epoch milliseconds
        time_from_ms = int(self._time_from.timestamp() * 1000)
        time_to_ms = int(self._time_to.timestamp() * 1000)
        
        # Apply variables to queries
        processed_queries = self._apply_variables_to_queries(queries)
        
        payload = {
            "queries": processed_queries,
            "from": str(time_from_ms),
            "to": str(time_to_ms)
        }
        
        response = self._session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def _apply_variables_to_queries(self, queries: List[Dict]) -> List[Dict]:
        """
        Replace variable placeholders with actual values from URL
        
        Args:
            queries: List of query configurations
            
        Returns:
            Queries with variables replaced
        """
        # Convert queries to JSON string for replacement
        queries_str = json.dumps(queries)
        
        # Replace each variable
        for var_name, var_value in self._variables.items():
            # Handle both ${var} and $var formats
            queries_str = queries_str.replace(f"${{{var_name}}}", var_value)
            queries_str = queries_str.replace(f"${var_name}", var_value)
            
            # Handle special Grafana variables
            if var_value == "$__all":
                queries_str = queries_str.replace(f"${{{var_name}}}", ".*")
        
        return json.loads(queries_str)
    
    def extract_panels_from_dashboard(self, dashboard: Dict) -> List[Dict]:
        """
        Extract all panels from dashboard JSON
        
        Returns:
            List of panel configurations with queries
        """
        panels = []
        dashboard_json = dashboard.get('dashboard', {})
        
        # Panels can be nested in rows
        for panel in dashboard_json.get('panels', []):
            if panel.get('type') == 'row':
                # Row panel contains nested panels
                panels.extend(panel.get('panels', []))
            else:
                panels.append(panel)
        
        return panels

