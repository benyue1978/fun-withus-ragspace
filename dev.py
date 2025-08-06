#!/usr/bin/env python3
"""
Simple development server with file watching
"""

import os
import sys
import time
import subprocess
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DevHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_app()
    
    def restart_app(self):
        """Restart the application"""
        if self.process:
            print("🔄 Restarting server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        env = os.environ.copy()
        env["DEV_MODE"] = "true"
        env["DEBUG"] = "true"
        
        print("🚀 Starting RAGSpace in development mode...")
        print("📝 Auto-reload enabled - changes to .py files will restart the server")
        print("🌐 Server will be available at: http://localhost:8000")
        print("🔧 MCP Server will be available at: http://localhost:8000/gradio_api/mcp/")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 60)
        
        self.process = subprocess.Popen(
            [sys.executable, "app.py"],
            env=env
        )
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Only watch Python files
        if not event.src_path.endswith('.py'):
            return
        
        print(f"🔄 File changed: {event.src_path}")
        self.restart_app()

def main():
    """Main development server"""
    handler = DevHandler()
    observer = Observer()
    observer.schedule(handler, path='.', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Development server stopped")
    finally:
        if handler.process:
            handler.process.terminate()
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main() 