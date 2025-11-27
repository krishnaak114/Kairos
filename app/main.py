"""
Main entry point for HeartbeatMonitor.

Supports two modes:
1. CLI mode: Process JSON file and output results
2. API mode: Run FastAPI server for production deployments (optional)

Examples:
    CLI mode:
        python app/main.py --file data/events.json --interval 60 --allowed-misses 3
    
    API mode:
        python app/main.py --api --port 8000
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Optional

from app.models import MonitorConfig
from app.monitor import HeartbeatMonitor
from app.utils import (
    setup_logging,
    load_events_from_file,
    save_alerts_to_file,
    print_summary
)

logger = logging.getLogger(__name__)


def main_cli(args: argparse.Namespace) -> int:
    """
    Run in CLI mode: process file and output results.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Load events from file
        logger.info(f"Loading events from: {args.file}")
        raw_events = load_events_from_file(args.file)
        logger.info(f"Loaded {len(raw_events)} events")
        
        # Create monitor configuration
        config = MonitorConfig(
            expected_interval_seconds=args.interval,
            allowed_misses=args.allowed_misses,
            tolerance_seconds=args.tolerance
        )
        
        # Initialize monitor and detect alerts
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(raw_events)
        
        # Print summary to console
        if not args.quiet:
            print_summary(result)
        
        # Save alerts to output file if specified
        if args.output:
            logger.info(f"Saving alerts to: {args.output}")
            save_alerts_to_file(result.alerts, args.output)
        
        # Output JSON to stdout if requested
        if args.json:
            # Simplified output format for the assignment
            alerts_json = [
                {
                    "service": alert.service,
                    "alert_at": alert.alert_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                }
                for alert in result.alerts
            ]
            print(json.dumps(alerts_json, indent=2))
        
        logger.info("Processing complete")
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        print(f"Error: Invalid JSON in input file - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main_api(args: argparse.Namespace) -> int:
    """
    Run in API mode: start FastAPI server (optional production feature).
    
    This is a bonus feature that turns the monitor into a REST API service.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code
    """
    try:
        import uvicorn
        from fastapi import FastAPI, File, UploadFile, HTTPException
        from fastapi.responses import JSONResponse
        from app.models import HealthCheckResponse
        
        # Create FastAPI application
        app = FastAPI(
            title="Kairós API",
            description="Production-grade service heartbeat monitoring - detecting issues at the opportune moment",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        @app.get("/", tags=["Root"])
        async def root():
            """Root endpoint with API information."""
            return {
                "name": "Kairós API",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/health",
                    "monitor": "/monitor",
                    "docs": "/docs"
                }
            }
        
        @app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
        async def health_check():
            """Health check endpoint."""
            return HealthCheckResponse(
                status="healthy",
                version="1.0.0"
            )
        
        @app.post("/monitor", tags=["Monitoring"])
        async def monitor_heartbeats(
            file: UploadFile = File(..., description="JSON file with heartbeat events"),
            interval: int = 60,
            allowed_misses: int = 3,
            tolerance: int = 0
        ):
            """
            Process heartbeat events and detect alerts.
            
            Upload a JSON file containing heartbeat events and receive alert results.
            """
            try:
                # Read and parse JSON file
                contents = await file.read()
                raw_events = json.loads(contents)
                
                # Create config and monitor
                config = MonitorConfig(
                    expected_interval_seconds=interval,
                    allowed_misses=allowed_misses,
                    tolerance_seconds=tolerance
                )
                monitor = HeartbeatMonitor(config)
                
                # Detect alerts
                result = monitor.detect_alerts(raw_events)
                
                # Return result as JSON
                return result.model_dump(mode='json')
                
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON file")
            except Exception as e:
                logger.error(f"Error processing request: {e}", exc_info=True)
                raise HTTPException(status_code=500, detail=str(e))
        
        # Run the server
        logger.info(f"Starting API server on http://0.0.0.0:{args.port}")
        print(f"\n⚡ Kairós API running on http://localhost:{args.port}")
        print(f"📚 API documentation available at http://localhost:{args.port}/docs\n")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=args.port,
            log_level=args.log_level.lower()
        )
        
        return 0
        
    except ImportError:
        logger.error("FastAPI dependencies not installed")
        print(
            "Error: FastAPI dependencies not installed.\n"
            "Install with: pip install fastapi uvicorn python-multipart",
            file=sys.stderr
        )
        return 1
    except Exception as e:
        logger.error(f"API server error: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        return 1


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Kairós - Service Heartbeat Monitor - Detect missed service heartbeats at the opportune moment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python app/main.py --file data/events.json --interval 60 --allowed-misses 3
  
  # With JSON output
  python app/main.py --file data/events.json --interval 60 --allowed-misses 3 --json
  
  # Save alerts to file
  python app/main.py --file data/events.json --interval 60 --allowed-misses 3 --output alerts.json
  
  # Run as API server (optional)
  python app/main.py --api --port 8000
        """
    )
    
    # Mode selection
    parser.add_argument(
        '--api',
        action='store_true',
        help='Run in API mode (requires FastAPI)'
    )
    
    # CLI mode arguments
    parser.add_argument(
        '--file',
        type=str,
        default='data/events.json',
        help='Path to JSON file with heartbeat events (default: data/events.json)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Expected interval between heartbeats in seconds (default: 60)'
    )
    parser.add_argument(
        '--allowed-misses',
        type=int,
        default=3,
        help='Number of consecutive misses before alert (default: 3)'
    )
    parser.add_argument(
        '--tolerance',
        type=int,
        default=0,
        help='Tolerance window in seconds for late heartbeats (default: 0)'
    )
    
    # Output options
    parser.add_argument(
        '--output',
        type=str,
        help='Save alerts to JSON file'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output alerts as JSON to stdout'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress summary output'
    )
    
    # API mode arguments
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for API server (default: 8000)'
    )
    
    # Logging options
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        help='Log to file'
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code
    """
    args = parse_arguments()
    
    # Setup logging
    setup_logging(level=args.log_level, log_file=args.log_file)
    
    # Route to appropriate mode
    if args.api:
        return main_api(args)
    else:
        return main_cli(args)


if __name__ == "__main__":
    sys.exit(main())
