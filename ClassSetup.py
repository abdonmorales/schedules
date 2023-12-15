"""
Script Name: ClassSetup.py
Author: Abdon Morales
Created: December 14, 2023
Last Modified: December 14, 2023
Version: 1.0

Description:
    This script fetches course data in JSON format from a specified GitHub repository.
    It presents the files in a Text-based User Interface (TUI) for selection. The selected
    course data is then used to synchronize directories in a OneDrive folder, creating new
    course directories and deleting old ones as necessary. Each course directory includes a
    text file with course details.

Dependencies:
    Requires the 'requests' library for fetching data from GitHub (pip install requests).
    The script uses 'curses' for the TUI, which is typically available in Unix-like environments.

Usage:
    Run the script in a Python environment with the necessary dependencies installed.
    Ensure that the GitHub repository URL and the OneDrive directory path are correctly set.

Contact:
    Abdon Morales
    abdonmorales@utexas.edu
"""

import requests
import json
import curses
from datetime import datetime
import os
import platform
import re
import shutil  # For deleting directories

# Function to get the list of JSON files in the Git repository
def get_json_files_from_git():
    git_repo_api_url = 'https://api.github.com/repos/abdonmorales/schedules/contents/Spring%202024'
    response = requests.get(git_repo_api_url)
    if response.status_code == 200:
        files = response.json()
        return [file for file in files if file['name'].endswith('.json')]
    else:
        raise Exception(f"Failed to get files: {response.status_code}")

# TUI for selecting a JSON file
def select_json_file(stdscr, files):
    curses.curs_set(0)
    cursor_position = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        stdscr.addstr(0, 0, "Select a JSON file for course data:\n\n")

        for i, file in enumerate(files):
            if i == cursor_position:
                stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(f"{i + 1}. {file['name']}\n")
            if i == cursor_position:
                stdscr.attroff(curses.A_REVERSE)

        stdscr.refresh()
        key = stdscr.getch()

        if key in [curses.KEY_ENTER, ord('\n')]:
            return files[cursor_position]['download_url']
        elif key == curses.KEY_UP and cursor_position > 0:
            cursor_position -= 1
        elif key == curses.KEY_DOWN and cursor_position < len(files) - 1:
            cursor_position += 1

# Function to download JSON file from a Git repository
def download_json_from_git(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to download file: {response.status_code}")

# Function to find the OneDrive directory
def find_onedrive_directory(base_path):
    pattern = re.compile(r'OneDrive.*', re.IGNORECASE)
    for root, dirs, files in os.walk(base_path):
        for name in dirs:
            if pattern.match(name):
                return os.path.join(root, name)
    return None

# Get the base path based on the operating system
def get_base_path():
    os_name = platform.system()
    if os_name == 'Windows':
        return os.environ['USERPROFILE']
    elif os_name == 'Darwin':  # macOS
        return os.path.expanduser('~')
    else:
        raise Exception("Unsupported operating system")

# Function to determine the upcoming semester based on the date
def determine_semester():
    month = datetime.now().month
    year = datetime.now().year
    if 11 <= month <= 12:
        return f"Spring {year + 1}"
    elif 6 <= month <= 10:
        return f"Fall {year}"
    else:
        return f"Summer {year}"

# Function to create a folder and a text file with course information
def create_folder_with_info(path, course_info):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Folder created: {path}")
        # Create a text file with course information
        info_file = os.path.join(path, "course_info.txt")
        with open(info_file, 'w') as f:
            for key, value in course_info.items():
                f.write(f"{key}: {value}\n")
        print(f"Info file created: {info_file}")
    else:
        print(f"Folder already exists: {path}")

# Function to get the list of existing course directories
def get_existing_directories(path):
    if not os.path.exists(path):
        return []
    return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

# Function to check if a directory is empty
def is_directory_empty(dir_path):
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        return not os.listdir(dir_path)
    return True  # If the path doesn't exist or isn't a directory, treat as empty

# Function to synchronize directories based on new schedule
def synchronize_directories(onedrive_path, semester_name, courses):
    semester_path = os.path.join(onedrive_path, semester_name)
    existing_dirs = get_existing_directories(semester_path)
    course_names = [course['coursename'] for course in courses]

    # Create directories and info files for new courses
    for course in courses:
        course_name = course['coursename']
        if course_name not in existing_dirs:
            course_folder_path = os.path.join(semester_path, course_name)
            create_folder_with_info(course_folder_path, course)

    # Delete directories for courses no longer in schedule
    for existing_dir in existing_dirs:
        if existing_dir not in course_names:
            dir_to_delete = os.path.join(semester_path, existing_dir)
            if is_directory_empty(dir_to_delete):
                shutil.rmtree(dir_to_delete)  # Safely delete the directory
                print(f"Deleted directory: {dir_to_delete}")
            else:
                print(f"Directory '{existing_dir}' is not empty and was not deleted.")

# Main execution
if __name__ == "__main__":
    try:
        # Fetch list of JSON files from GitHub
        json_files = get_json_files_from_git()

        # Use TUI to select a JSON file
        selected_file_url = curses.wrapper(select_json_file, json_files)
        print(f"Selected JSON file: {selected_file_url}")

        # Download the selected JSON file
        courses = download_json_from_git(selected_file_url)

        # Find and synchronize folders in OneDrive
        base_path = get_base_path()
        onedrive_path = find_onedrive_directory(base_path)
        if onedrive_path is None:
            raise Exception("OneDrive directory not found")

        semester_name = determine_semester()
        synchronize_directories(onedrive_path, semester_name, courses)

        print("Course folder synchronization complete.")

    except Exception as e:
        print(f"An error occurred: {e}")