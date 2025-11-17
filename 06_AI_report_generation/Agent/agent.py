#!/usr/bin/env python3
"""
Performance Report Agent - Main Entry Point

Usage:
    python agent.py "http://localhost:3000/d/dashboard-uid?from=...&to=..."
    python agent.py --url "http://localhost:3000/d/dashboard-uid?from=...&to=..."
"""

import sys
import argparse
from pathlib import Path

from src.agent import PerformanceReportAgent


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate AI-powered performance test reports from Grafana dashboards',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py "http://localhost:3000/d/abc123?from=2025-11-17T21:54:08.137Z&to=2025-11-17T22:05:41.904Z"
  
  python agent.py --url "http://localhost:3000/d/abc123?from=...&to=..."
  
  python agent.py --url "http://localhost:3000/d/abc123?from=...&to=..." --output-dir ./reports

Environment Variables Required:
  OPENAI_API_KEY          - OpenAI API key for AI analysis
  SERVICE_ACCOUNT_TOKEN   - Grafana service account token
        """
    )
    
    parser.add_argument(
        'url',
        nargs='?',
        help='Grafana dashboard URL with time range'
    )
    parser.add_argument(
        '--url',
        dest='url_flag',
        help='Grafana dashboard URL (alternative to positional argument)'
    )
    parser.add_argument(
        '--output-dir',
        default='./reports',
        help='Output directory (default: ./reports)'
    )
    
    args = parser.parse_args()
    
    # Get URL from either positional or flag argument
    dashboard_url = args.url or args.url_flag
    
    if not dashboard_url:
        parser.print_help()
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # Run agent
        print("=" * 60)
        print("🚀 Performance Report Agent")
        print("=" * 60)
        print()
        
        agent = PerformanceReportAgent()
        report_path = agent.generate_report(
            dashboard_url=dashboard_url,
            output_dir=args.output_dir
        )
        
        print("\n" + "=" * 60)
        print("✅ Report generated successfully!")
        print(f"📄 Location: {report_path}")
        print("=" * 60)
        print()
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Error: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

