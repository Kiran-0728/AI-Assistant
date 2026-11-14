"""
Main entry point for AI Assistant (Root launcher).
Delegates directly to inner AI_Assistant package.
"""
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sub_dir = os.path.join(script_dir, "AI_Assistant")
if os.path.exists(sub_dir):
    os.chdir(sub_dir)
    sys.path.insert(0, sub_dir)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--voice", "--cli", "-c"]:
        print("Starting AI Assistant in Voice Console mode...")
        import Assistant
        Assistant.run_assistant()
    else:
        print("Starting AI Assistant Desktop GUI...")
        import Assistant_GUI
        Assistant_GUI.launch()
