Tests for apt.py
----------------

**.\Expected** - output of the correctly working commands (manually managed)

**.\Current** - what the command is currently emitting. Overwritten on every test run.

**.\Broken** - commands not emitting the expected text (manually managed).



`test all` tests everything

`test help` invokes `apt help`  
`test list-installed` invokes `apt list-installed`
etc.

When complete WinMerge is called to compare the folders.


