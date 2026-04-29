#!/usr/bin/env python3
"""Start the Kaiwhakarite Rawa FastAPI server from the root directory"""

import uvicorn
import sys
import os
import logging

def main():
    """Start the server"""
    try:
        logging.basicConfig(level=logging.INFO)
        logging.info("🚀 Starting Kaiwhakarite Rawa Backend Server...")
        logging.info("📍 Server will be available at: http://localhost:8000")
        logging.info("📚 API Documentation at: http://localhost:8000/docs")
        logging.info("🔍 Health check at: http://localhost:8000/health")
        logging.info("⏹️  Press Ctrl+C to stop the server")
        logging.info("-" * 50)
        
        # Get the current working directory
        current_dir = os.getcwd()
        logging.info(f"📂 Current directory: {current_dir}")
        
        # Ensure we're in the project root directory
        if not os.path.exists('backend'):
            logging.error("❌ Error: 'backend' directory not found. Please run this script from the project root directory.")
            sys.exit(1)
        
        # Set PYTHONPATH environment variable to include the current directory
        os.environ['PYTHONPATH'] = current_dir
        logging.info(f"🔧 Set PYTHONPATH to: {current_dir}")
        
        # Start the server with the correct module path
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logging.info("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"❌ Error starting server: {e}")
        logging.error(f"📂 Current directory: {os.getcwd()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 