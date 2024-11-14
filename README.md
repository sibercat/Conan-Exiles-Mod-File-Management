Executable can be found in [Releases](https://github.com/sibercat/ConanExiles_ModFileManagement/releases) If your going to use .exe the executable was created by PyInstaller so you could get a false positive, you know the deal.

===========================================================================

![alt text](https://cdn.discordapp.com/attachments/517436895387451399/1306518180918984704/image.png?ex=6736f560&is=6735a3e0&hm=fda4938e204350e8462fe804999a61c96977031cbe7e6d89d4261e582eb93743&)

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
