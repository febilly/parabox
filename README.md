This is a (incomplete) clone of Patrick's Parabox for the calculator HP Prime.
![Screenshot](doc/screenshot.png)
This is a work in progress. Currently only the first 10 chapters from the original game are supported (I don't know if I'm going to support more chapters).

# Installation:
- Download this repository and install `Patrick's Parabox`
- Use [AssetStudio](https://github.com/Perfare/AssetStudio/releases) to extract all the TextAsset from
`Patricks Parabox\Patrick's Parabox_Data\resources.assets`
and put them(\*.txt files) in
`tools\extractor\input`
- Run `tools\extractor\extractor.py`
- Copy everything in `tools\extractor\output` to `release\box.hpappdir`
- Install `box.hpappdir` to your HP Prime using HP Connectivity Kit

# Controls:
- Move: arrow keys or `ab/c` `TAN` `LN` `LOG`
- Undo: `Backspace` (Note: You can undo a reset)
- Restart: `Esc`

# Known issues:
- The game will crash after several manual level selection due to OOM (decompression is very memory hungry and for some reason the memory decompression uses won't be freed up by gc? idk). To alleviate the problem, Try increasing the heap size and stack size.

# Credits:
- Patrick Traynor for [Patrick's Parabox](https://store.steampowered.com/app/1260520/Patricks_Parabox/)
- iwVerve for [Parafox](https://github.com/iwVerve/Parafox)
- Perfare for [AssetStudio](https://github.com/Perfare/AssetStudio)
- Nayuki for [Simple DEFLATE decompressor](https://github.com/nayuki/Simple-DEFLATE-decompressor) (MIT License)