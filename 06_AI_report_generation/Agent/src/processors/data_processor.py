"""Data processor for Grafana panel data"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from ..parsers.url_parser import GrafanaDashboardContext


@dataclass
class PanelData:
    """Processed panel data"""
    panel_id: int
    panel_title: str
    panel_type: str
    metrics: Dict[str, Any]
    raw_data: Dict[str, Any]


class DataProcessor:
    """Process and aggregate Grafana panel data"""
    
    def process_panel_data(
        self,
        panel_config: Dict[str, Any],
        raw_data: Dict[str, Any],
        context: GrafanaDashboardContext
    ) -> PanelData:
        """
        Process panel data and extract metrics
        
        Args:
            panel_config: Panel configuration from dashboard
            raw_data: Raw query results from Grafana
            context: Dashboard context
            
        Returns:
            Processed panel data with metrics
        """
        panel_id = panel_config.get('id', 0)
        panel_title = panel_config.get('title', 'Untitled')
        panel_type = panel_config.get('type', 'unknown')
        
        # Extract and calculate metrics
        metrics = self._extract_metrics(raw_data, panel_type)
        
        return PanelData(
            panel_id=panel_id,
            panel_title=panel_title,
            panel_type=panel_type,
            metrics=metrics,
            raw_data=raw_data
        )
    
    def _extract_metrics(self, raw_data: Dict[str, Any], panel_type: str) -> Dict[str, Any]:
        """
        Extract metrics from raw panel data
        
        Args:
            raw_data: Raw query results
            panel_type: Type of panel (graph, stat, table, etc.)
            
        Returns:
            Dictionary of calculated metrics
        """
        metrics = {}
        
        try:
            results = raw_data.get('results', {})
            
            # Iterate through query results
            for ref_id, result in results.items():
                frames = result.get('frames', [])
                
                for frame in frames:
                    schema = frame.get('schema', {})
                    data_values = frame.get('data', {}).get('values', [])
                    
                    if len(data_values) >= 2:
                        # Typically: [timestamps, values]
                        timestamps = data_values[0]
                        values = data_values[1]
                        
                        if values:
                            # Calculate basic statistics
                            numeric_values = [v for v in values if v is not None and isinstance(v, (int, float))]
                            
                            if numeric_values:
                                metrics[ref_id] = {
                                    'min': min(numeric_values),
                                    'max': max(numeric_values),
                                    'avg': sum(numeric_values) / len(numeric_values),
                                    'count': len(numeric_values),
                                    'latest': numeric_values[-1] if numeric_values else None
                                }
        except Exception as e:
            metrics['error'] = str(e)
        
        return metrics

