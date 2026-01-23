import PyInstaller.__main__
import os
import shutil

# --- CONFIGURATION ---
MAIN_SCRIPT = "main.py"
EXE_NAME = "MixerApp"
# List of (Source, Destination) for data files and folders
DATA_FILES = [
    ("blueprints", "blueprints"),
    ("services", "services"),
    ("static", "static"),
    ("nircmd.exe", "."),
    ("adb.exe", "."),
]


def build():
    # Construct the --add-data arguments based on OS (Windows uses ;)
    add_data_args = []
    for src, dest in DATA_FILES:
        if os.path.exists(src):
            add_data_args.extend(["--add-data", f"{src}{os.pathsep}{dest}"])
        else:
            print(f"Warning: {src} not found, skipping...")

    # PyInstaller Arguments
    args = [
        MAIN_SCRIPT,
        "--name", EXE_NAME,
        "--onefile",        # Bundle into a single EXE
        "--windowed",       # No console window
        "--noconfirm",      # Overwrite existing build folders
        "--clean",          # Clean cache before building
    ] + add_data_args

    print(f"Starting build for {EXE_NAME}...")
    PyInstaller.__main__.run(args)
    print("\nBuild complete! Check the 'dist' folder for your executable.")


if __name__ == "__main__":
    build()