# apt
_A command line package manager for [Osgeo4W](http://trac.osgeo.org/osgeo4w/)_

This is the development repository for the [apt package](http://trac.osgeo.org/osgeo4w/wiki/pkg-apt). It's a perpetual beta project, run by someone who's learning to program in python (very slowly!). That said, I've been using it regularly for several years to install and maintain o4w systems without serious problems. It works, more or less.

Apt uses the same configuration files as the mainline Osgeo4wSetup.exe, so either tool can be used to install and remove packages at will (but not concurrently!).

Daily use:

    apt update                   (fetch up-to-date setup.ini)
    apt install gdal gdal-python (install packages "gdal" and "gdal-python", and dependencies)
    apt new                      (show possible upgrades)
    apt list                     (show installed packages)
    apt available                (show installation candidates)
    apt remove xxx yyy           (uninstall packages xxx and yyy)


##From scratch
Apt can also be used to install [a virgin Osgeo4W system from scratch](http://trac.osgeo.org/osgeo4w/wiki/pkg-apt/AptFromScratch):

Download the latest release from https://github.com/maphew/apt/releases/. Open a CMD shell and:

    SET OSGEO4W_ROOT=C:\Osgeo4Wx64
    apt --bits=64 setup
    apt update
    apt install shell

32bit:

    SET OSGEO4W_ROOT=C:\Osgeo4W
    apt --bits=32 setup
    apt update
    apt install shell


## Differences from Setup.exe
Apt strives to match Setup's results as closely as possible, and to not screw anything up that Setup does. User's should never be put in a position where they feel the need to choose between the tools and not go back. 

That's the aspiration. There's no guarantee it's been achieved.

Where I know we depart from Setup:

 - `etc/setup/timestamp` apt doesn't create or use this file, while Setup does. Presumably it is to avoid downloading a new package list on every invocation, only when older than X. Apt doesn't need this since it has it's own `apt update` command that's fired at user discretion. Issue #15.

- Apt doesn't know about the `%OSGEO4W_MENU_LINKS%` and `%OSGEO4W_DESKTOP_LINKS%` variables introduced in setup.exe v1.0.6-5. This needs to be added, issue #16. 


### Contributors and Contributing ###

These fine people have made this program better than I could have managed on my own:

- Andreas Müller (@amr66), Universitaet Trier, Germany (64bit handdling, improved return signals, exception handling, lots of other stuff); 
- Jeremy Palmer, Land Information New Zealand (dependencies 1st, menu name);   
- Luke Pinner, Australia Department of the Environment, Water, Heritage and the Arts (windows special folders);  
- Jan Nieuwenhuizen (original cyg-apt author). 

If you'd like to help, see **[the code](https://github.com/maphew/apt/)** and auto-generated **module docs**: http://apt.readthedocs.org/en/latest/

### Similar projects ###

- [cyg-apt](http://www.lilypond.org/~janneke/software/cyg-apt), the original python script by Jan Nieuwenhuizen that started it all.
- [cyg-apt](https://code.google.com/p/cyg-apt/) - a fork by cjcormie, dev stopped ~2009
- [apt-cyg](https://github.com/transcode-open/apt-cyg) - written in bash by transcode-open; relatively active and current.
