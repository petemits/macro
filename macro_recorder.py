#!/usr/bin/env python3
"""
WORKING BROWSER MACRO RECORDER - No keyboard module needed
Records your actions and plays them back
"""

import pyautogui
import time
import json
import threading
from datetime import datetime
from pathlib import Path
import sys

class BrowserMacroRecorder:
    def __init__(self):
        self.recording = False
        self.playing = False
        self.macro_actions = []
        self.macro_file = "browser_macro.json"
        self.stop_flag = False
        
    def record_macro(self):
        """Record mouse and keyboard actions"""
        print("\n" + "="*60)
        print("🎥 MACRO RECORDER - Recording Mode")
        print("="*60)
        print("\nINSTRUCTIONS:")
        print("1. Switch to your browser after pressing Enter")
        print("2. Perform your actions (clicks, typing, etc.)")
        print("3. Press Ctrl+C in this window to STOP recording")
        print("\nGet ready to record...")
        print("="*60)
        
        input("\nPress Enter to START recording and switch to browser...")
        
        # Give time to switch to browser
        print("\n🔴 Starting in 3 seconds... Switch to browser NOW!")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        self.start_recording()
    
    def start_recording(self):
        """Start recording actions"""
        self.recording = True
        self.macro_actions = []
        self.stop_flag = False
        start_time = time.time()
        
        print("\n🔴 RECORDING STARTED! Performing actions in browser...")
        print("Press Ctrl+C in THIS window to STOP recording")
        
        last_mouse_pos = pyautogui.position()
        last_action_time = start_time
        last_click_time = 0
        
        # Store initial clipboard content
        import pyperclip
        initial_clipboard = pyperclip.paste()
        
        try:
            while self.recording and not self.stop_flag:
                current_time = time.time()
                current_pos = pyautogui.position()
                
                # Detect left mouse click
                if pyautogui.mouseDown(button='left'):
                    current_click_time = time.time()
                    # Debounce: ignore clicks too close together
                    if current_click_time - last_click_time > 0.3:
                        action = {
                            'type': 'click',
                            'x': current_pos.x,
                            'y': current_pos.y,
                            'button': 'left',
                            'time_since_last': current_time - last_action_time
                        }
                        self.macro_actions.append(action)
                        last_action_time = current_time
                        last_click_time = current_click_time
                        print(f"📌 Click recorded at ({current_pos.x}, {current_pos.y})")
                    time.sleep(0.1)  # Small delay after click
                
                # Detect right mouse click
                elif pyautogui.mouseDown(button='right'):
                    action = {
                        'type': 'right_click',
                        'x': current_pos.x,
                        'y': current_pos.y,
                        'button': 'right',
                        'time_since_last': current_time - last_action_time
                    }
                    self.macro_actions.append(action)
                    last_action_time = current_time
                    print(f"🖱️ Right click at ({current_pos.x}, {current_pos.y})")
                    time.sleep(0.1)
                
                # Detect typing by checking clipboard changes (simple approach)
                # This captures Ctrl+C/Ctrl+V operations
                try:
                    current_clipboard = pyperclip.paste()
                    if current_clipboard != initial_clipboard:
                        action = {
                            'type': 'paste',
                            'text': current_clipboard,
                            'time_since_last': current_time - last_action_time
                        }
                        self.macro_actions.append(action)
                        last_action_time = current_time
                        print(f"📋 Text captured: {current_clipboard[:50]}...")
                        initial_clipboard = current_clipboard
                except:
                    pass  # Clipboard access might fail, that's OK
                
                # Record significant mouse movements
                if (abs(current_pos.x - last_mouse_pos.x) > 20 or 
                    abs(current_pos.y - last_mouse_pos.y) > 20):
                    action = {
                        'type': 'move',
                        'x': current_pos.x,
                        'y': current_pos.y,
                        'time_since_last': current_time - last_action_time
                    }
                    # Only record significant moves to avoid clutter
                    if len(self.macro_actions) == 0 or self.macro_actions[-1]['type'] != 'move':
                        self.macro_actions.append(action)
                        print(f"↗️  Move to ({current_pos.x}, {current_pos.y})")
                    last_mouse_pos = current_pos
                
                # Small sleep to reduce CPU usage
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n⏹️ Recording stopped by user")
            self.recording = False
        
        print("\n✅ Recording finished!")
        self.save_macro()
    
    def save_macro(self):
        """Save macro to file"""
        if not self.macro_actions:
            print("❌ No actions recorded!")
            return
        
        # Filter out some move actions to keep macro clean
        filtered_actions = []
        for i, action in enumerate(self.macro_actions):
            if action['type'] == 'move':
                # Only keep moves that are followed by clicks
                if i + 1 < len(self.macro_actions) and self.macro_actions[i + 1]['type'] in ['click', 'right_click']:
                    filtered_actions.append(action)
            else:
                filtered_actions.append(action)
        
        self.macro_actions = filtered_actions
        
        macro_data = {
            'created': datetime.now().isoformat(),
            'actions': self.macro_actions,
            'total_actions': len(self.macro_actions)
        }
        
        with open(self.macro_file, 'w') as f:
            json.dump(macro_data, f, indent=2)
        
        print(f"✅ Macro saved to {self.macro_file}")
        print(f"📊 Actions recorded: {len(self.macro_actions)}")
        
        # Show summary
        click_count = sum(1 for a in self.macro_actions if a['type'] in ['click', 'right_click'])
        move_count = sum(1 for a in self.macro_actions if a['type'] == 'move')
        paste_count = sum(1 for a in self.macro_actions if a['type'] == 'paste')
        
        print(f"   Clicks: {click_count}")
        print(f"   Moves: {move_count}")
        print(f"   Text operations: {paste_count}")
        
        print("\n" + "="*60)
        print("🎬 PLAYBACK INSTRUCTIONS:")
        print("1. Make sure browser is in SAME POSITION as when recording")
        print("2. Select 'Play macro' from menu")
        print("3. Switch to browser within 3 seconds")
        print("="*60)
    
    def play_macro(self):
        """Play back recorded macro"""
        print("\n" + "="*60)
        print("▶️ MACRO PLAYBACK")
        print("="*60)
        
        # Load macro
        if not Path(self.macro_file).exists():
            print(f"❌ No macro found! Record one first")
            return
        
        with open(self.macro_file, 'r') as f:
            try:
                macro_data = json.load(f)
            except:
                print("❌ Error loading macro file")
                return
        
        actions = macro_data.get('actions', [])
        
        if not actions:
            print("❌ Macro has no actions")
            return
        
        print(f"\n📁 Playing macro with {len(actions)} actions")
        print("⏱️ Starting in 3 seconds... Switch to browser!")
        
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print("\n▶️ PLAYING... (Press Ctrl+C to stop)")
        
        self.playing = True
        self.stop_flag = False
        
        try:
            for i, action in enumerate(actions):
                if not self.playing or self.stop_flag:
                    break
                
                # Wait between actions
                wait_time = action.get('time_since_last', 0.5)
                if wait_time > 0:
                    time.sleep(wait_time)
                
                # Perform action
                if action['type'] == 'click':
                    print(f"📍 Action {i+1}/{len(actions)}: Click at ({action['x']}, {action['y']})")
                    pyautogui.moveTo(action['x'], action['y'], duration=0.2)
                    pyautogui.click()
                
                elif action['type'] == 'right_click':
                    print(f"🖱️ Action {i+1}: Right click at ({action['x']}, {action['y']})")
                    pyautogui.moveTo(action['x'], action['y'], duration=0.2)
                    pyautogui.rightClick()
                
                elif action['type'] == 'move':
                    print(f"↗️  Action {i+1}: Move to ({action['x']}, {action['y']})")
                    pyautogui.moveTo(action['x'], action['y'], duration=0.3)
                
                elif action['type'] == 'paste':
                    text = action.get('text', '')
                    if text:
                        print(f"📋 Action {i+1}: Paste text ({len(text)} chars)")
                        import pyperclip
                        pyperclip.copy(text)
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(0.2)
                
        except KeyboardInterrupt:
            print("\n🛑 Playback stopped by user")
        except Exception as e:
            print(f"\n❌ Playback error: {e}")
        
        print("\n✅ Playback completed!")
        self.playing = False
    
    def show_macro_info(self):
        """Show information about saved macro"""
        if not Path(self.macro_file).exists():
            print("❌ No macro recorded yet")
            return
        
        with open(self.macro_file, 'r') as f:
            try:
                macro_data = json.load(f)
            except:
                print("❌ Error reading macro file")
                return
        
        actions = macro_data.get('actions', [])
        created = macro_data.get('created', 'Unknown')
        
        print(f"\n📊 MACRO INFORMATION:")
        print(f"   Created: {created}")
        print(f"   Total actions: {len(actions)}")
        
        click_count = sum(1 for a in actions if a['type'] in ['click', 'right_click'])
        move_count = sum(1 for a in actions if a['type'] == 'move')
        paste_count = sum(1 for a in actions if a['type'] == 'paste')
        
        print(f"   Clicks: {click_count}")
        print(f"   Moves: {move_count}")
        print(f"   Text operations: {paste_count}")
        
        # Show first few actions
        if actions:
            print(f"\n📝 First 5 actions:")
            for i, action in enumerate(actions[:5]):
                if action['type'] == 'click':
                    print(f"   {i+1}. Click at ({action['x']}, {action['y']})")
                elif action['type'] == 'move':
                    print(f"   {i+1}. Move to ({action['x']}, {action['y']})")
                elif action['type'] == 'paste':
                    text_preview = action.get('text', '')[:30]
                    print(f"   {i+1}. Paste: {text_preview}...")
    
    def auto_type_text(self, text, delay=0.1):
        """Type text character by character"""
        print(f"⌨️  Typing: {text[:50]}...")
        pyautogui.write(text, interval=delay)
    
    def create_scheduled_task(self):
        """Create Windows scheduled task"""
        print("\n⏰ WINDOWS TASK SCHEDULER SETUP")
        print("="*60)
        
        script_path = Path(__file__).absolute()
        python_exe = sys.executable
        
        print(f"\n📁 Script path: {script_path}")
        print(f"🐍 Python: {python_exe}")
        
        print("\n📋 MANUAL SETUP INSTRUCTIONS:")
        print("1. Open 'Task Scheduler' (search in Start menu)")
        print("2. Click 'Create Basic Task'")
        print("3. Name: 'Auto Newsletter'")
        print("4. Trigger: Daily at your preferred time")
        print(f"5. Action: Start program: {python_exe}")
        print(f"6. Arguments: \"{script_path}\" --play")
        print("7. Check 'Run whether user is logged on or not'")
        print("8. Make sure browser is open at scheduled time")
        
        print("\n⚠️  IMPORTANT:")
        print("- Browser must be OPEN and VISIBLE when task runs")
        print("- Browser window should be in SAME POSITION as when recording")
        print("- Test with 'Play macro' first to ensure it works")
        
        input("\nPress Enter to continue...")
    
    def run_interactive(self):
        """Run interactive mode"""
        print("\n" + "="*60)
        print("🤖 SIMPLE BROWSER MACRO RECORDER")
        print("="*60)
        print("\nOPTIONS:")
        print("  1. Record new macro")
        print("  2. Play existing macro")
        print("  3. View macro info")
        print("  4. Setup scheduled task (Windows)")
        print("  5. Exit")
        
        while True:
            try:
                choice = input("\nSelect option (1-5): ").strip()
                
                if choice == '1':
                    self.record_macro()
                elif choice == '2':
                    self.play_macro()
                elif choice == '3':
                    self.show_macro_info()
                elif choice == '4':
                    self.create_scheduled_task()
                elif choice == '5':
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice. Please enter 1-5.")
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

def check_install():
    """Check and install required packages"""
    print("🔧 Checking required packages...")
    
    missing_packages = []
    
    # Check pyautogui
    try:
        import pyautogui
        print("✅ pyautogui installed")
    except ImportError:
        missing_packages.append('pyautogui')
    
    # Check pyperclip for clipboard operations
    try:
        import pyperclip
        print("✅ pyperclip installed")
    except ImportError:
        missing_packages.append('pyperclip')
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing...")
        
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("✅ Packages installed successfully!")
            print("\n🔄 RESTART the script to continue")
            input("Press Enter to exit...")
            sys.exit(0)
        except:
            print("❌ Failed to install packages")
            print(f"Please run manually: pip install {' '.join(missing_packages)}")
            input("Press Enter to exit...")
            sys.exit(1)
    
    return True

def main():
    """Main function"""
    print("\n" + "="*60)
    print("🤖 BROWSER MACRO RECORDER")
    print("Ready to record and replay your browser actions!")
    print("="*60)
    
    # Check installations
    if not check_install():
        return
    
    # Create recorder and run
    recorder = BrowserMacroRecorder()
    recorder.run_interactive()

if __name__ == "__main__":
    main()