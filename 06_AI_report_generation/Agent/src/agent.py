"""Main performance report agent orchestrator"""

import os
from typing import List
from dotenv import load_dotenv

from .parsers.url_parser import GrafanaURLParser, GrafanaDashboardContext
from .clients.grafana_client import GrafanaClient
from .clients.openai_client import OpenAIClient
from .processors.data_processor import DataProcessor, PanelData
from .builders.report_builder import ReportBuilder


class PerformanceReportAgent:
    """Main orchestrator for performance report generation"""
    
    def __init__(self):
        """Initialize the agent with required components"""
        # Load environment variables
        load_dotenv()
        
        # Validate environment
        self._validate_environment()
        
        # Initialize components (composition over inheritance)
        self._url_parser = GrafanaURLParser()
        self._data_processor = DataProcessor()
        self._openai_client = OpenAIClient()
        self._report_builder = ReportBuilder()
    
    def _validate_environment(self) -> None:
        """Validate required environment variables are set"""
        required_vars = ['OPENAI_API_KEY', 'SERVICE_ACCOUNT_TOKEN']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please set them in your .env file or environment"
            )
    
    def generate_report(
        self, 
        dashboard_url: str,
        output_dir: str = './reports'
    ) -> str:
        """
        Generate performance test report from Grafana dashboard URL
        
        Args:
            dashboard_url: Full Grafana dashboard URL with time range
            output_dir: Directory to save report
            
        Returns:
            Path to generated report file
        """
        print("📊 Parsing dashboard URL...")
        context = self._parse_url(dashboard_url)
        
        print(f"✓ Dashboard: {context.dashboard_uid}")
        print(f"✓ Time Range: {self._url_parser.get_time_range_description(context)}")
        print(f"✓ Variables: {len(context.variables)} found")
        
        print("\n🔌 Connecting to Grafana...")
        grafana_client = GrafanaClient(context)
        
        print("📥 Fetching dashboard data...")
        dashboard = grafana_client.get_dashboard()
        dashboard_title = dashboard['dashboard']['title']
        print(f"✓ Dashboard: {dashboard_title}")
        
        print("\n🎛️  Processing panels...")
        panels = grafana_client.extract_panels_from_dashboard(dashboard)
        print(f"✓ Found {len(panels)} panels")
        
        panel_data_list = self._process_panels(grafana_client, panels, context)
        
        print(f"\n🤖 Analyzing data with AI...")
        ai_analysis = self._analyze_with_ai(panel_data_list, context, dashboard_title)
        
        print("\n📄 Building report...")
        report = self._report_builder.build_report(
            dashboard_title=dashboard_title,
            context=context,
            panel_data_list=panel_data_list,
            ai_analysis=ai_analysis
        )
        
        print("💾 Exporting report...")
        output_path = self._report_builder.export(
            report=report,
            output_dir=output_dir,
            filename=f"performance_report_{context.dashboard_uid}_{context.time_from.strftime('%Y%m%d_%H%M%S')}"
        )
        
        # Print report to stdout for CI/CD visibility
        print("\n" + "=" * 80)
        print("📄 GENERATED REPORT")
        print("=" * 80)
        print(report)
        print("=" * 80)
        
        return output_path
    
    def _parse_url(self, dashboard_url: str) -> GrafanaDashboardContext:
        """Parse dashboard URL to extract context"""
        return self._url_parser.parse(dashboard_url)
    
    def _process_panels(
        self,
        grafana_client: GrafanaClient,
        panels: List[dict],
        context: GrafanaDashboardContext
    ) -> List[PanelData]:
        """Process all panels and extract metrics"""
        panel_data_list = []
        
        for i, panel in enumerate(panels, 1):
            panel_title = panel.get('title', 'Untitled')
            print(f"  [{i}/{len(panels)}] {panel_title}")
            
            try:
                # Fetch panel data
                raw_data = grafana_client.get_panel_data(
                    panel_id=panel['id'],
                    datasource_uid=context.variables.get(
                        'data_source', 
                        panel.get('datasource', {}).get('uid', '')
                    ),
                    queries=panel.get('targets', [])
                )
                
                # Process and aggregate metrics
                processed_data = self._data_processor.process_panel_data(
                    panel_config=panel,
                    raw_data=raw_data,
                    context=context
                )
                
                panel_data_list.append(processed_data)
                
            except Exception as e:
                print(f"  ⚠️  Warning: Failed to process panel: {e}")
                continue
        
        return panel_data_list
    
    def _analyze_with_ai(
        self,
        panel_data_list: List[PanelData],
        context: GrafanaDashboardContext,
        dashboard_title: str
    ) -> str:
        """Analyze panel data using AI"""
        # Prepare data summary for AI
        data_summary = self._prepare_data_summary(panel_data_list, context)
        
        # Create prompt for AI analysis
        system_prompt = """You are a performance testing expert analyzing Grafana dashboard metrics.
Provide a concise executive summary of the performance test results.
Focus on key findings, trends, potential issues, and recommendations."""
        
        user_prompt = f"""Analyze the following performance test results:

Dashboard: {dashboard_title}
Time Range: {self._url_parser.get_time_range_description(context)}

Metrics Summary:
{data_summary}

Please provide:
1. Overall performance assessment
2. Key findings and trends
3. Any concerns or anomalies
4. Recommendations for improvement
"""
        
        return self._openai_client.analyze(user_prompt, system_prompt)
    
    def _prepare_data_summary(
        self,
        panel_data_list: List[PanelData],
        context: GrafanaDashboardContext
    ) -> str:
        """Prepare data summary for AI analysis"""
        summary_lines = []
        
        for panel_data in panel_data_list:
            summary_lines.append(f"\n{panel_data.panel_title} ({panel_data.panel_type}):")
            
            if panel_data.metrics:
                for ref_id, metrics in panel_data.metrics.items():
                    if isinstance(metrics, dict) and 'error' not in metrics:
                        summary_lines.append(f"  - {ref_id}: Min={metrics.get('min')}, Max={metrics.get('max')}, Avg={metrics.get('avg', 0):.2f}")
            else:
                summary_lines.append("  - No metrics available")
        
        return "\n".join(summary_lines)

