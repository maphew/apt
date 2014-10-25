# apt
_A command line package manager for [Osgeo4W](http://trac.osgeo.org/osgeo4w/)_

This is the development repository for the [apt package](http://trac.osgeo.org/osgeo4w/wiki/pkg-apt). It's a perpetual beta project, run by someone who's learning to program in python (very slowly!). That said, I've been using it regularly for several years to install and maintain o4w systems without serious problems. It works, more or less.

Apt uses the same configuration files as the mainline Osgeo4wSetup.exe, so either tool can be used to install and remove packages at will (but not at the same time!).

At the moment, apt can only install the 32bit Osgeo4W packages.

Daily use:

    apt update                   (fetch up-to-date setup.ini)
    apt install gdal gdal-python (install packages "gdal" and "gdal-python", and dependencies)
    apt new                      (show possible upgrades)
    apt list                     (show installed packages)
    apt available                (show installation candidates)
    apt remove xxx yyy           (uninstall packages xxx and yyy)


##From scratch
Apt can also be used to install [a virgin Osgeo4W system from scratch](http://trac.osgeo.org/osgeo4w/wiki/pkg-apt/AptFromScratch):

Download the latest apt-rxx.exe from  http://download.osgeo.org/osgeo4w/release/apt/. If you like rename to apt.exe. Open a CMD shell and:

    SET OSGEO4W_ROOT=C:\Osgeo4W
    apt setup
    apt update
    apt install shell


### Contributors ###

These fine people have made this program better than I could have managed on my own:

- Jeremy Palmer, Land Information New Zealand (dependencies 1st, menu name);   
- Luke Pinner, Australia Department of the Environment, Water, Heritage and the Arts (windows special folders);  
- Jan Nieuwenhuizen (original cyg-apt author). 

### Similar projects ###

- [cyg-apt](http://www.lilypond.org/~janneke/software/cyg-apt), the original python script by Jan Nieuwenhuizen that started it all.
- [cyg-apt](https://code.google.com/p/cyg-apt/) - a fork by cjcormie, dev stopped ~2009
- [apt-cyg](https://github.com/transcode-open/apt-cyg) - written in bash by transcode-open; relatively active and current.

