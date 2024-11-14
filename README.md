Executable can be found in [Releases](https://github.com/sibercat/ConanExiles_ModFileManagement/releases) If your going to use .exe the executable was created by PyInstaller so you could get a false positive, you know the deal.

===========================================================================

![alt text](https://cdn.discordapp.com/attachments/517436895387451399/1306514221219057704/image.png?ex=6736f1b0&is=6735a030&hm=09dd313f83e137170642ab4cb071755a3215e6af91f82f30bad0eb8f46ac0d34&)

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
