"""
Quick test: verify that _beside_exe() correctly finds alert.wav next to the exe.
Run this from the dist/ folder to simulate how the .exe behaves.
"""
import os, sys, winsound

def _beside_exe(filename):
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)

sound_path = _beside_exe("alert.wav")
print(f"Looking for sound at: {sound_path}")

if os.path.exists(sound_path):
    print("✓ alert.wav FOUND — playing it now...")
    winsound.PlaySound(sound_path, winsound.SND_FILENAME)
    print("✓ Sound played successfully!")
else:
    print("✗ alert.wav NOT FOUND — would fall back to Windows default sound")
    print("  Playing default Windows sound instead...")
    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
    print("✓ Default sound played")
