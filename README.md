# Overview

This file system crawler, as the name implies, recursively crawls through a given input directory and gathers metadata about visited files and stores them into a "data store". 

The gathered metadata includes:

* The file's absolute path
* The file's parent directory name
* The file's UID
* The file's GID
* The file's "ctime"
* The file's last accessed time
* The file's last modified time
* The current operating system

The "ctime" is different depending on what operating system we are on. On Linux, ctime is the last time the file inode was modified. On Windows, ctime is the creation time.

The file's UID and GID are also different depending on what operating system we are on. On Windows, these values will be lengthy strings called "security descriptors" (SIDs), and in Linux they are simply integer identifiers for the file owner's user ID (UID) and the file's group (GID). The UID and GID in Windows are the file owner's SID and the primary group owner's SID.

# Data Stores

Data stores are where the crawler stores the gathered file metadata. Currently, the only type of data store outputs the results as a CSV (i.e. the `CsvDataStore` class) but the crawler is flexible enough to easily swap out different types of data stores so you could use, for example, a SQLite database instead of a CSV file.

To create a new data store, all you have to do is:

1. Create a class that inherits from the `DataStore` class and implements the initialize, insert, and finalize abstract methods
2. In the `datastore_factory` module, add your new data store type to the DataStoreEnum
3. In the `datastore_factory` module, modify the `create` method to create your new DataStore instance based on the passed in DataStoreEnum type

And that's it! You do not need to modify any other code to add a new DataStore type.

# Script Arguments

| Argument Flags                        | Description                                                                                               | Required? | Default         |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------- | --------- | --------------- |
| `-h`, `--help`                        | Show help message and exit                                                                                | No        | N/A             |
| `-i INPUT`, `--input INPUT`           | The input directory to crawl through                                                                      | Yes       | N/A             |
| `-o OUTPUT`, `--output OUTPUT`        | The directory to the store the results. If it does not exist, it will be created for you                  | No        | "output"        |
| `-fn FILENAME`, `--filename FILENAME` | The name of the output file. This does not include the ext. Place "%s" where you want the timestamp to go | No        | "%s__fsc-output"|
| `-d {csv}`, `--datastore {csv}`       | The type of the output, i.e. the data store                                                               | No        | "csv"           |

In order to get an up-to-date version of the arguments that are passed in to the module, all you have to do is type:
```
#!bash

python filesystemcrawler --help
```
And you should get a listing of the different arguments that can be passed in.

# Example Invocations

A very simple invocation that will crawl through the '/projects' directory:
```
#!bash

python filesystemcrawler -i '/projects'
```

Changing the output directory to "csv_output" when crawling in input directory "/projects":
```
#!bash

python filesystemcrawler -i '/projects' -o 'csv_output'
```

# Known issues and future improvements

## Known Windows Issue With Mounted Filesystems
The Windows implementations of getting usernames, "UIDs", and "GIDs" is imperfect because you do not get a complete picture of file permissions if a mounted filesystem doesn't support security descriptors. For example, some mounted SAMBA shares or VirtualBox's shared folders may not be supported. If a file descriptor cannot be loaded, then it defaults to "Everyone". Link to issue: http://support.microsoft.com/kb/243330

## Script Feedback
Currently, the script does not provide any feedback when running. Given that you may crawl through some enormous file systems, it would be better if a progress metric was presented to the user. This is planned for in future versions.

## Different Types of Data Stores
Currently, the script only supports CSV data stores. SQLite is planned to be built in soon.


-------------------------------------------------------------------------------

** Script Author:** Angela Gross










