import os
import shutil
import pyttsx3
import speech_recognition as sr
from tqdm import tqdm
import threading
import time
import sys
import random

class Colors:
    RESET = "\033[0m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[3].id)
engine.setProperty("rate", 170)
engine.setProperty("volume", 1)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()
    
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")
            return ""

def spinner():
    """Function to display a spinning wheel while the backup is in progress."""
    while not stop_spinner_event.is_set():
        for cursor in '|/-\\':
            sys.stdout.write(f'\r{cursor} Backing up...')
            sys.stdout.flush()
            time.sleep(0.1)

def backup_files(source_dirs, backup_dirs):
    """
    Copies files from specified source directories to backup directories.

    :param source_dirs: List of source directories to back up.
    :param backup_dirs: List of directories where files will be backed up.
    """
    for backup_dir in backup_dirs:
        os.makedirs(backup_dir, exist_ok=True)

    for source_dir in source_dirs:
        print(f"Checking source directory: {source_dir}")
        if os.path.exists(source_dir):
            print(f"Source directory exists: {source_dir}")
            dir_name = os.path.basename(os.path.normpath(source_dir))

            items = os.listdir(source_dir)
            total_items = len(items)
            print(f"Items in {source_dir}:")

            for item in items:
                print(f" - {item}") # Displays the item in the terminal

            for backup_dir in backup_dirs:
                target_dir = os.path.join(backup_dir, dir_name)
                os.makedirs(target_dir, exist_ok=True)

                with tqdm(total=total_items, desc=f"{Colors.GREEN}Backing up {dir_name}{Colors.RESET}", 
                          bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} items", ncols=100) as pbar:
                   
                    spinner_thread = threading.Thread(target=spinner)
                    spinner_thread.start()

                    for item in items:
                        source_item = os.path.join(source_dir, item)
                        target_item = os.path.join(target_dir, item)

                        try:
                            if os.path.isfile(source_item):
                                # Replaces the old files with new ones
                                shutil.copy2(source_item, target_item)
                            elif os.path.isdir(source_item):
                                
                                if os.path.exists(target_item):
                                    shutil.rmtree(target_item)  
                                shutil.copytree(source_item, target_item)
                        except Exception as e:
                            print(f"Error copying {source_item} to {target_item}: {e}")

                        pbar.update(1)

                    stop_spinner_event.set()
                    spinner_thread.join()

                print(f"Backup completed for: {source_dir} to {target_dir}")
                speak(f"Backup completed")
        else:
            print(f"Source directory does not exist: {source_dir}")
            speak(f"The source directory does not exist")

def perform_backup():
    global stop_spinner_event
    stop_spinner_event = threading.Event()

    source_directories = [
        "FILEPATH THAT WILL BE COPIED FROM"
    ]
    
    backup_directories = [
        "TARGET FOLDER TO RECEIVE FILES"
    ]
    
    start_phrases = [ # Phrases that will be spoken once copy starts, only one each time
        "Backup is starting now.",
        "Initiating backup process.",
        "Starting the backup, please wait.",
        "Backup in progress, hold on.",
        "Let's begin the backup.",
        "Commencing backup now."
    ]

    announcement = random.choice(start_phrases) # Selects a phrase
    speak(announcement)

    print("Available folders to back up:")
    for index, folder in enumerate(source_directories):
        print(f"{index + 1}: {folder}")

    selected_folders = source_directories

    backup_files(selected_folders, backup_directories)

    stop_spinner_event.set()

def main():
    global stop_spinner_event
    stop_spinner_event = threading.Event() 

    perform_backup()

if __name__ == "__main__":
    main()
