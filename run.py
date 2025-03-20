#!/usr/bin/env python3
"""
ROM Analysis System Runner
-------------------------
This script provides a convenient way to run different components of the ROM analysis system.

Usage:
    python run.py [component] [options]

Components:
    api         - Run the FastAPI server
    demo        - Run the basic demo with webcam
    holistic    - Run the holistic demo with webcam
    help        - Show this help message

Options:
    --port PORT       - Port to run the API server (default: 8000)
    --host HOST       - Host to run the API server (default: 0.0.0.0)
    --source SOURCE   - Camera index or video file for demos (default: 0)
    --output OUTPUT   - Output video file for demos (optional)
    --complexity N    - Model complexity for holistic (0, 1, or 2) (default: 1)
"""

import os
import sys
import argparse
import subprocess
import webbrowser
import time

def parse_args():
    parser = argparse.ArgumentParser(description="ROM Analysis System Runner")
    
    parser.add_argument('component', type=str, choices=['api', 'demo', 'holistic', 'help'],
                        help='Component to run')
    
    # API options
    parser.add_argument('--port', type=int, default=8000,
                        help='Port to run the API server (default: 8000)')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Host to run the API server (default: 0.0.0.0)')
    parser.add_argument('--reload', action='store_true',
                        help='Enable auto-reload for API server')
    
    # Demo options
    parser.add_argument('--source', type=str, default='0',
                        help='Camera index or video file for demos (default: 0)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output video file for demos (optional)')
    parser.add_argument('--complexity', type=int, default=1, choices=[0, 1, 2],
                        help='Model complexity for holistic (0, 1, or 2) (default: 1)')
    parser.add_argument('--width', type=int, default=1280,
                        help='Video width (default: 1280)')
    parser.add_argument('--height', type=int, default=720,
                        help='Video height (default: 720)')
    
    return parser.parse_args()

def run_api_server(args):
    """Run the FastAPI server"""
    print(f"Starting API server on http://{args.host}:{args.port}")
    
    # Check if templates directory exists
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("Created templates directory")
    
    # Check if index.html exists in templates
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>ROM Analysis API</title>
    <meta http-equiv="refresh" content="0;url=/docs">
</head>
<body>
    <p>Redirecting to API documentation...</p>
</body>
</html>""")
        print("Created redirect page to API docs")
    
    # Construct the uvicorn command
    cmd = [
        "uvicorn", 
        "app:app", 
        "--host", args.host, 
        "--port", str(args.port)
    ]
    
    if args.reload:
        cmd.append("--reload")
    
    try:
        # Open browser to the API docs
        time.sleep(1)  # Give the server a moment to start
        webbrowser.open(f"http://localhost:{args.port}/docs")
        
        # Run the server
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down API server")
    except Exception as e:
        print(f"Error starting API server: {e}")

def run_basic_demo(args):
    """Run the basic ROM demo"""
    print(f"Starting ROM Analysis Demo with source: {args.source}")
    
    cmd = [
        "python", 
        "demo.py",
        "--source", args.source
    ]
    
    if args.output:
        cmd.extend(["--output", args.output])
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down demo")
    except Exception as e:
        print(f"Error running demo: {e}")

def run_holistic_demo(args):
    """Run the holistic ROM demo"""
    print(f"Starting Holistic ROM Analysis Demo with source: {args.source}")
    
    cmd = [
        "python", 
        "holistic_demo.py",
        "--source", args.source,
        "--complexity", str(args.complexity),
        "--width", str(args.width),
        "--height", str(args.height)
    ]
    
    if args.output:
        cmd.extend(["--output", args.output])
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down holistic demo")
    except Exception as e:
        print(f"Error running holistic demo: {e}")

def show_help():
    """Show help message"""
    print(__doc__)

def main():
    args = parse_args()
    
    if args.component == 'api':
        run_api_server(args)
    elif args.component == 'demo':
        run_basic_demo(args)
    elif args.component == 'holistic':
        run_holistic_demo(args)
    elif args.component == 'help':
        show_help()
    else:
        print(f"Unknown component: {args.component}")
        show_help()

if __name__ == "__main__":
    main()