# Data

'Data' directory for World of Warcraft custom Data changes such as Sounds or Fonts.

Merge this files into Data directory (or just patch-Y.MPQ file alone) to get profit:

- Creature/ replacement for Ghosts (Lady Deathwhisper ICC fight)
- Fonts/ for cyrillic charset
- Sound/ replacement for annoying sounds e.g. Goblin Weather Machine, Argent Gruntling/Squire, Lament of the Highborne song, Fizzle spell sounds, Character voice emotions
- [patch-Y.MPQ](https://github.com/grandatlant/DataMod/blob/main/patch-Y.MPQ) itself with all contents above

Additional content besides patch:

- 'realmlist.wtf' for warmane.com private server
- [script](https://github.com/grandatlant/DataMod/blob/main/pack_patch_mpq.py) for packing all files from Creature/, Fonts/, Sound/ to one 'patch-Y.MPQ'
- [script](https://github.com/grandatlant/DataMod/blob/main/remove-unused-sv.py) for SavedVariables cleanup in your WTF/ (stolen from [Soulsbane](https://github.com/Soulsbane/WowRemoveUnusedSV) with WoW path override to "../")
