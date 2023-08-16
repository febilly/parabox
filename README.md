This is a (incomplete) clone of Patrick's Parabox for the calculator HP Prime.
![Screenshot](doc/screenshot.png)
This is a work in progress. Currently only the main chapters from the original game are supported.

# Installation:
- Download this repository and install `Patrick's Parabox`
- Use [AssetStudio](https://github.com/Perfare/AssetStudio/releases) to extract all the TextAsset from
`Patricks Parabox\Patrick's Parabox_Data\resources.assets`
and put them(\*.txt files) in
`tools\extractor\input`
- Run `tools\extractor\extractor.py`
- Copy everything in `tools\extractor\output` to `release\box.hpappdir`
- Install `box.hpappdir` to your HP Prime using HP Connectivity Kit

# For running on PC:
- Do the same as above except for the last step
- Install [Python](https://www.python.org) and [pygame library](https://www.pygame.org/docs/) (and optionally [HP Prime Virtual Calculator Emulator](https://www.hpcalc.org/details/8939))
- Copy `hpprime.py` (from `/src`) (and optionally `PrimeSansFull.ttf` (from `C:\Program Files\HP\HP Prime Virtual Calculator\fonts`)) to `release\box.hpappdir`
- Double click `main.py` to run
- On PC, use arrow keys to move, `Backspace` to undo, and `Esc` to restart

# Controls:
- Move: arrow keys or `ab/c` `TAN` `LN` `LOG`
- Undo: `Backspace` (Note: You can undo a reset)
- Restart: `Esc`

# Known issues:
- The game will crash after several manual level selection due to OOM (decompression is very memory hungry and for some reason the memory decompression uses won't be freed by gc? idk). To alleviate the problem, Try increasing the heap size and stack size.
- images won't scale down properly.

# Credits:
- Patrick Traynor for [Patrick's Parabox](https://store.steampowered.com/app/1260520/Patricks_Parabox/)
- iwVerve for [Parafox](https://github.com/iwVerve/Parafox)
- Perfare for [AssetStudio](https://github.com/Perfare/AssetStudio)
- Nayuki for [Simple DEFLATE decompressor](https://github.com/nayuki/Simple-DEFLATE-decompressor) (MIT License)
- nana and geerky42 for [this steam community guide (Direction Input Walkthrough)](https://steamcommunity.com/sharedfiles/filedetails/?id=2786724419)
