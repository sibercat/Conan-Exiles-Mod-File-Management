#V0.0.10
import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Any
from pathlib import Path

class ConfigManager:
    def __init__(self, config_file: str = 'file_manager_config.json'):
        self.config_file = config_file
        self.config_backup = f'{config_file}.backup'
        self.default_config = {
            'log_file_path': '',
            'search_directory': '',
            'content_directory': '',
            'last_modified': '',
            'backup_directory': '',
            'file_extensions_filter': [],
            'orphaned_file_threshold': 1024  # Default to 1KB
        }
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return {**self.default_config, **config}
        except json.JSONDecodeError:
            print("Error reading config file. Loading default configuration.")
        except Exception as e:
            print(f"Error loading config: {e}")
        return self.default_config.copy()

    def save_config(self, config: Dict[str, Any]) -> bool:
        try:
            if os.path.exists(self.config_file):
                shutil.copy2(self.config_file, self.config_backup)
            
            config['last_modified'] = datetime.now().isoformat()
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

def parse_comparison_file(file_path: str) -> Dict[str, List[str]]:
    """
    Parse a file comparison text file that contains sections for Deleted, Added, and Changed files.
    Returns a dictionary with three lists of file paths.
    """
    sections = {
        'Deleted': [],
        'Added': [],
        'Changed': []
    }
    
    current_section = None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and divider lines
            if not line or line.startswith('--'):
                continue
                
            # Check for section headers
            if line == 'Deleted':
                current_section = 'Deleted'
                continue
            elif line == 'Added':
                current_section = 'Added'
                continue
            elif line == 'Changed':
                current_section = 'Changed'
                continue
            # Skip the version info line
            elif line.startswith('Asset changes between'):
                continue
                
            # If we're in a section and have a valid line, add it to the appropriate list
            if current_section and line:
                sections[current_section].append(line)
                
        return sections
        
    except FileNotFoundError:
        print(f"Error: Could not find file '{file_path}'")
        return sections
    except Exception as e:
        print(f"Error reading file: {e}")
        return sections

def load_target_files_from_comparison(file_path: str, include_sections: List[str] = None) -> List[str]:
    """
    Load target filenames from a comparison file, optionally filtering by section.
    
    Args:
        file_path (str): Path to the comparison file
        include_sections (List[str]): List of sections to include ['Deleted', 'Added', 'Changed'].
                                    If None, includes all sections.
    
    Returns:
        List[str]: List of unique filenames to process
    """
    sections = parse_comparison_file(file_path)
    
    if not include_sections:
        include_sections = ['Deleted', 'Added', 'Changed']
        
    target_files = set()
    for section in include_sections:
        if section in sections:
            target_files.update(sections[section])
            
    return list(target_files)

def format_size(size: int) -> str:
    """Convert size in bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

def get_path_with_default(prompt: str, default_value: str) -> str:
    """Get path from user with default value option."""
    if default_value:
        print(f"Current saved path: {default_value}")
        use_default = input("Use this path? (y/n): ").lower() == 'y'
        if use_default:
            return default_value
    return input(prompt)

def extract_filenames(log_file: str) -> List[str]:
    """Extract paths starting from 'Content/Mods/' from the log file."""
    file_paths = []
    try:
        with open(log_file, 'r', encoding='utf-8') as file:
            for line in file:
                if 'Missing cooked file:' in line:
                    start_idx = line.find('Content/Mods/')
                    if start_idx != -1:
                        # Extract everything after 'Content/Mods/'
                        path = line[start_idx:].strip().strip("'")
                        file_paths.append(path)
                        
    except FileNotFoundError:
        print(f"Error: Could not find log file '{log_file}'")
        return []
    return file_paths

def search_files(search_path: str, file_paths: List[str], config: Dict[str, Any]) -> List[Tuple[str, int]]:
    """Search for files using Content/Mods/... paths with strict path matching and size warning."""
    found_files = []
    abs_path = os.path.abspath(search_path)
    print(f"\nSearching in: {abs_path}")
    
    # Define size threshold for potential orphaned files (1KB = 1024 bytes)
    ORPHANED_FILE_THRESHOLD = config.get('orphaned_file_threshold', 1024)  # Default to 1KB if not in config
    
    for content_path in file_paths:
        try:
            # Normalize the target path
            normalized_target = content_path.split('Content/Mods/')[-1].replace('/', os.sep)
            filename = os.path.basename(normalized_target)
            print(f"\nSearching for: {filename}")
            print(f"Expected path: {normalized_target}")
            
            for root, _, files in os.walk(abs_path):
                for file in files:
                    if file.lower() == filename.lower():
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, abs_path).replace('\\', '/')
                        
                        # Extract the part after Content/Mods/ or Local/ for comparison
                        if '/Local/' in rel_path:
                            compare_path = rel_path.split('/Local/')[-1]
                        else:
                            compare_path = rel_path.split('/Content/Mods/')[-1]
                            
                        # Split paths into components for comparison
                        target_components = normalized_target.replace('\\', '/').split('/')
                        found_components = compare_path.split('/')
                        
                        if 'Local' in found_components:
                            found_components.remove('Local')
                            
                        # Compare the directory structure
                        if target_components[-3:] == found_components[-3:]:
                            size = os.path.getsize(full_path)
                            found_files.append((full_path, size))
                            
                            # Add clear indication if file is likely an orphaned file
                            if size < ORPHANED_FILE_THRESHOLD:
                                print(f"Found match (LIKELY ORPHANED FILE): {full_path}")
                                print(f"Size: {size} bytes - This appears to be a leftover file from UE4 deletion")
                            else:
                                print(f"Found match: {full_path}")
                                print(f"Size: {size} bytes")
                            
                            print(f"Path components matched: {' -> '.join(target_components[-3:])}")
                        else:
                            print(f"Skipping potential false positive: {full_path}")
                            print(f"Expected path components: {' -> '.join(target_components[-3:])}")
                            print(f"Found path components: {' -> '.join(found_components[-3:])}")
                        
        except OSError as e:
            print(f"Error accessing path: {e}")
    
    # Sort files with orphaned files first
    found_files.sort(key=lambda x: (x[1] >= ORPHANED_FILE_THRESHOLD, x[1]))
    
    # Add summary of orphaned files
    orphaned_count = sum(1 for _, size in found_files if size < ORPHANED_FILE_THRESHOLD)
    if orphaned_count > 0:
        print(f"\nFound {orphaned_count} potential orphaned files (size < 1KB)")
        print("These are likely leftover files from UE4 asset deletion and can be safely removed")
    
    return found_files

def delete_files(files_to_delete: List[Tuple[str, int]]) -> Tuple[int, List[str]]:
    """Delete files and return the number of successfully deleted files."""
    success_count = 0
    failed_deletions = []
    
    for file_path, _ in files_to_delete:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
            success_count += 1
        except OSError as e:
            print(f"Error deleting {file_path}: {e}")
            failed_deletions.append(file_path)
    
    return success_count, failed_deletions

def find_matching_files(directory: str, target_files: List[str]) -> List[Tuple[str, int]]:
    """Search for specific files in the directory and return matches with their sizes."""
    matching_files = []
    print(f"\nSearching in directory: {directory}")
    print("Looking for the following files:")
    for file in target_files[:5]:  # Show first 5 files
        print(f"- {file}")
    if len(target_files) > 5:
        print(f"... and {len(target_files) - 5} more files")
    print("\nSearching...")

    try:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower() in [os.path.basename(target).lower() for target in target_files]:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    matching_files.append((file_path, file_size))
                    print(f"Found match: {file_path}")

    except Exception as e:
        print(f"Error scanning directory: {e}")
        return []

    return matching_files

def display_matching_results(files_info: List[Tuple[str, int]]) -> None:
    """Display information about matching files found."""
    if not files_info:
        print("No matching files found.")
        return

    print(f"\nTotal matching files found: {len(files_info)}")
    
    # Sort files by size (largest first)
    sorted_files = sorted(files_info, key=lambda x: x[1], reverse=True)
    
    print("\nMatching files found (sorted by size):")
    for idx, (file_path, size) in enumerate(sorted_files, 1):
        print(f"{idx}. {file_path}")
        print(f"   Size: {format_size(size)}")

def main():
    """Main entry point with direct file management functionality."""
    config_manager = ConfigManager()
    config = config_manager.config

    while True:
        print("Conan Exiles Mod File Manager By Sibercat V0.0.10")
        print("\nMenu Options:")
        print("1. Search for missing cooked files and delete")
        print("2. View current configuration")
        print("3. Update configuration")
        print("4. Find patch modified files")
        print("q. Quit")
        
        choice = input("Enter your choice: ")
        
        if choice.lower() == 'q':
            break
            
        elif choice == '1':
            # Get log file path
            log_file = get_path_with_default(
                "Please enter the path to your log file: ",
                config['log_file_path']
            )
            
            if log_file != config['log_file_path']:
                config['log_file_path'] = log_file
                config_manager.save_config(config)

            # Extract and process files
            file_paths = extract_filenames(log_file)
            if not file_paths:
                print("No files to search for were found in the log file.")
                continue

            print("\nFound the following files to search for:")
            for path in file_paths:
                print(f"- {path}")

            # Get search directory
            search_dir = get_path_with_default(
                "\nEnter path to your ConanSandbox/Content/Mods directory: ",
                config['search_directory']
            )
            
            if search_dir != config['search_directory']:
                config['search_directory'] = search_dir
                config_manager.save_config(config)

            # Search for files
            found_files = search_files(search_dir, file_paths, config)
            if not found_files:
                print("\nNo matching files were found.")
                continue

            # Display found files
            print("\nFound files:")
            for idx, (file_path, file_size) in enumerate(found_files, 1):
                print(f"{idx}. {file_path}")
                print(f"   Size: {format_size(file_size)}")

            # File management loop
            while found_files:
                print("\nFile Management Options:")
                print("1. Delete individual file (enter file number)")
                print("2. Delete all files")
                print("q. Return to main menu")
                
                subchoice = input("Enter your choice: ")
                
                if subchoice.lower() == 'q':
                    break
                    
                elif subchoice == '1':
                    try:
                        file_idx = int(input("Enter file number to delete: ")) - 1
                        if 0 <= file_idx < len(found_files):
                            file_to_delete = found_files[file_idx]
                            confirm = input(f"Are you sure you want to delete '{file_to_delete[0]}'? (y/n): ")
                            
                            if confirm.lower() == 'y':
                                success_count, failed = delete_files([file_to_delete])
                                if success_count > 0:
                                    print(f"Successfully deleted: {file_to_delete[0]}")
                                    found_files.pop(file_idx)
                        else:
                            print("Invalid file number.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                elif subchoice == '2':
                    confirm = input(f"Are you sure you want to delete ALL {len(found_files)} files? (y/n): ")
                    if confirm.lower() == 'y':
                        success_count, failed = delete_files(found_files)
                        print(f"\nSuccessfully deleted {success_count} out of {len(found_files)} files.")
                        if failed:
                            print("\nFailed to delete the following files:")
                            for file_path in failed:
                                print(f"- {file_path}")
                        found_files = [(f, s) for f, s in found_files if os.path.exists(f)]
                
                else:
                    print("Invalid choice. Please try again.")
        
        elif choice == '2':
            print("\nCurrent Configuration:")
            for key, value in config.items():
                print(f"{key}: {value}")
        
        elif choice == '3':
            print("\nUpdating Configuration")
            for key in config:
                if key != 'last_modified':
                    print(f"\nCurrent {key}: {config[key]}")
                    new_value = input(f"Enter new value for {key} (or press Enter to keep current): ")
                    if new_value:
                        config[key] = new_value
            config_manager.save_config(config)
            print("Configuration updated successfully!")
        
        elif choice == '4':
            content_dir = get_path_with_default(
                "Enter the directory to scan: ",
                config.get('content_directory', '')
            )
            
            if not os.path.exists(content_dir):
                print("Error: Directory does not exist.")
                continue
            
            if content_dir != config.get('content_directory'):
                config['content_directory'] = content_dir
                config_manager.save_config(config)
                
            # New file loading section
            target_files_path = input("Enter the path to your comparison file: ")
            
            # Ask which sections to include
            print("\nWhich sections would you like to process?")
            print("1. All sections")
            print("2. Only Deleted files")
            print("3. Only Added files")
            print("4. Only Changed files")
            print("5. Custom combination")
            
            section_choice = input("Enter your choice (1-5): ")
            
            if section_choice == '1':
                include_sections = ['Deleted', 'Added', 'Changed']
            elif section_choice == '2':
                include_sections = ['Deleted']
            elif section_choice == '3':
                include_sections = ['Added']
            elif section_choice == '4':
                include_sections = ['Changed']
            elif section_choice == '5':
                include_sections = []
                if input("Include Deleted files? (y/n): ").lower() == 'y':
                    include_sections.append('Deleted')
                if input("Include Added files? (y/n): ").lower() == 'y':
                    include_sections.append('Added')
                if input("Include Changed files? (y/n): ").lower() == 'y':
                    include_sections.append('Changed')
            else:
                print("Invalid choice. Processing all sections.")
                include_sections = ['Deleted', 'Added', 'Changed']

            target_files = load_target_files_from_comparison(target_files_path, include_sections)

            if not target_files:
                print("No valid files found in the provided comparison file.")
                continue

            print(f"\nProcessing files from sections: {', '.join(include_sections)}")
            print(f"Total files to process: {len(target_files)}")
            print("\nSample of files to process:")
            for file in target_files[:5]:  # Show first 5 files
                print(f"- {file}")
            if len(target_files) > 5:
                print(f"... and {len(target_files) - 5} more files")

            matching_files = find_matching_files(content_dir, target_files)
            
            if matching_files:
                display_matching_results(matching_files)
                
                # File management loop
                while matching_files:
                    print("\nFile Management Options:")
                    print("1. Delete individual file (enter file number)")
                    print("2. Delete all matching files")
                    print("q. Return to main menu")
                    
                    subchoice = input("Enter your choice: ")
                    
                    if subchoice.lower() == 'q':
                        break
                        
                    elif subchoice == '1':
                        try:
                            file_idx = int(input("Enter file number to delete: ")) - 1
                            if 0 <= file_idx < len(matching_files):
                                file_to_delete = matching_files[file_idx]
                                confirm = input(f"Are you sure you want to delete '{file_to_delete[0]}'? (y/n): ")
                                
                                if confirm.lower() == 'y':
                                    success_count, failed = delete_files([file_to_delete])
                                    if success_count > 0:
                                        print(f"Successfully deleted: {file_to_delete[0]}")
                                        matching_files.pop(file_idx)
                            else:
                                print("Invalid file number.")
                        except ValueError:
                            print("Please enter a valid number.")
                    
                    elif subchoice == '2':
                        confirm = input(f"Are you sure you want to delete ALL {len(matching_files)} files? (y/n): ")
                        if confirm.lower() == 'y':
                            success_count, failed = delete_files(matching_files)
                            print(f"\nSuccessfully deleted {success_count} out of {len(matching_files)} files.")
                            if failed:
                                print("\nFailed to delete the following files:")
                                for file_path in failed:
                                    print(f"- {file_path}")
                            matching_files = [(f, s) for f, s in matching_files if os.path.exists(f)]
                    
                    else:
                        print("Invalid choice. Please try again.")
            else:
                print("No matching files found in the specified directory.")
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
