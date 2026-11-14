"""
Main entry point for AI Assistant.
Can be run via PyCharm, VS Code, double-clicking, or command line without any terminal requirements.
"""

import sys
import os

if __name__ == "__main__":
    # If explicitly requested voice-only console mode
    if len(sys.argv) > 1 and sys.argv[1] in ["--voice", "--cli", "-c"]:
        print("Starting AI Assistant in Voice Console mode...")
        import Assistant
        Assistant.run_assistant()
    else:
        # Default to the sleek Desktop GUI
        print("Starting AI Assistant Desktop GUI...")
        import Assistant_GUI
        Assistant_GUI.launch()
