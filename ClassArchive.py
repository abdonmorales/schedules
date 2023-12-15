"""
Script Name: ClassArchive.py
Author: Abdon Morales
Created: December 14, 2023
Last Modified: December 14, 2023
Version: 1.0

Description:
    This script allows the user to select a semester folder from the OneDrive directory
    and archive it into a zip file. The user can select the semester folder using a
    Text-based User Interface (TUI). The archived zip file is saved to a specified
    directory.

Dependencies:
    Uses 'curses' for the TUI, which is typically available in Unix-like environments.

Usage:
    Before running the script, ensure the OneDrive directory and the target archive directory
    are correctly set. Run the script in a Python environment where 'curses' is available.

Contact:
    Abdon Morales
    abdonmorales@utexas.edu
"""

import os
import zipfile
import curses


# Function to find directories that contain 'OneDrive' in their name
def find_onedrive_directories(base_path):
    return [os.path.join(base_path, d) for d in os.listdir(base_path) if
            'OneDrive' in d and os.path.isdir(os.path.join(base_path, d))]


# TUI for selecting a directory
def select_directory(stdscr, title, directories):
    curses.curs_set(0)
    cursor_position = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        stdscr.addstr(0, 0, f"{title}:\n\n")

        for i, dir in enumerate(directories):
            if i == cursor_position:
                stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(f"{i + 1}. {dir}\n")
            if i == cursor_position:
                stdscr.attroff(curses.A_REVERSE)

        stdscr.refresh()
        key = stdscr.getch()

        if key in [curses.KEY_ENTER, ord('\n')]:
            return directories[cursor_position]
        elif key == curses.KEY_UP and cursor_position > 0:
            cursor_position -= 1
        elif key == curses.KEY_DOWN and cursor_position < len(directories) - 1:
            cursor_position += 1


# Function to list semester directories in a given directory
def list_directories(path):
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]


# Function to archive a directory
def archive_directory(dir_path, archive_path):
    zip_filename = os.path.join(archive_path, f"{os.path.basename(dir_path)}.zip")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(dir_path, '..')))

    print(f"Archived '{dir_path}' to '{zip_filename}'.")


# Main execution
if __name__ == "__main__":
    try:
        base_path = os.path.expanduser('~')
        onedrive_directories = find_onedrive_directories(base_path)
        if not onedrive_directories:
            raise Exception("No OneDrive directory found")

        onedrive_path = curses.wrapper(select_directory, "Select OneDrive directory", onedrive_directories)
        semester_directories = list_directories(onedrive_path)
        selected_semester = curses.wrapper(select_directory, "Select semester directory to archive",
                                           semester_directories)

        archive_path = "/Volumes/Austin Disk/UT Austin/"
        archive_directory(os.path.join(onedrive_path, selected_semester), archive_path)

    except Exception as e:
        print(f"An error occurred: {e}")