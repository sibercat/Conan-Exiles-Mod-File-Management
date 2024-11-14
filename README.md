I got tired of manually searching for 1KB Missing cooked files after cooking and made this little script.

I added 4. Files matching for anyone that overwrites vanilla assets 

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
