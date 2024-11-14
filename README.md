Executable can be found in [Releases](https://github.com/sibercat/SibercatsLauncher/releases) If your going to use .exe the executable was created by PyInstaller so you could get a false positive, you know the deal.

I got tired of manually searching for 1KB Missing cooked files after cooking and made this little script.

I added 4. Find patch modified files |  for anyone that overwrites vanilla assets | just point to your Mods\Content | point or drop asset_changes.txt and it will do its magic

Core Functionalities

1. **Missing Cooked Files Detection**
   - Parses log files for "Missing cooked file" entries
   - Focuses on paths starting with 'Content/Mods/'
   - Case-insensitive file matching

2. **File Search System**
   - Recursive directory scanning
   - Smart path matching considering mod structure
   - Size calculation and formatting
   - Path relativity handling

3. **File Management**
   - Individual and batch file deletion
   - Confirmation prompts for safety
   - Error handling and reporting
   - Success/failure tracking
