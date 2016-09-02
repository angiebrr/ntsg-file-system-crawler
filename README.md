# Dependencies

- Python 3.5
- tqdm 4.8

# Overview

This file system crawler, as the name implies, recursively crawls through a given input directory and gathers metadata about visited files and stores them into a "data store". 

## Gathered Metadata

Note that the "ctime" is different depending on what operating system we are on. On Linux, ctime is the last time the file inode was modified. On Windows, ctime is the creation time.

The file's UID and GID are also different depending on what operating system we are on. On Windows, these values will be lengthy strings called "security descriptors" (SIDs), and in Linux they are simply integer identifiers for the file owner's user ID (UID) and the file's group (GID). The UID and GID in Windows are the file owner's SID and the primary group owner's SID.

### v1.0 (Up to August 18th 2016)

| Column Name              | Description                                                   |
| ------------------------ | ------------------------------------------------------------- |
| `full_file_parent_path`  | The file parent directory's absolute path                     |
| `file_name`              | The file's name (stem) without its "suffix" (extension)       |
| `file_ext`               | The file's extension                                          |
| `file_size`              | The file's size (in bytes)                                    |
| `file_uid`               | The file's UID                                                |
| `file_gid`               | The file's GID                                                |
| `file_ctime`             | The file's "ctime"                                            |
| `file_accessed_time`     | The file's last accessed time                                 |
| `file_modified_time`     | The file's last modified time                                 |
| `current_os`             | The current operating system                                  |

### v2.0 (Current)

| Column Name              | Description                                                   |
| ------------------------ | ------------------------------------------------------------- |
| `full_file_parent_path`  | The file parent directory's absolute path                     |
| `file_mode`              | The file's "mode" {DIR, FILE, SYM}                            |
| `file_name`              | The file's name (stem) without its "suffix" (extension)       |
| `file_ext`               | The file's extension                                          |
| `file_size_in_bytes`     | The file's size (in bytes)                                    |
| `file_uid`               | The file's UID                                                |
| `file_gid`               | The file's GID                                                |
| `file_ctime`             | The file's "ctime"                                            |
| `file_accessed_time`     | The file's last accessed time                                 |
| `file_modified_time`     | The file's last modified time                                 |
| `file_real_path`         | If it's a SYM file, the file's "real path" or target path     |
| `current_os`             | The current operating system                                  |

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

# Logging

A file is created with the same name (but ".log" extension) as the output file and is placed in the output directory. 

The following things are logged:

* When the crawler begins (it includes the input and output directories and the data store type)
* When an error occurs during either crawling or data store finalizing
* When an error occurs when processing a file
* When a file is not processed because it's a symbolic link or a shortcut (a ".lnk" file in Windows)
* When the crawl ends and the data store is finalized

It includes a message and a timestamp that may look something like this:


```
#!bash
# /crawler_output/my-dir-crawl_Aug-17-2016_10-59-50.log

INFO:root:[2016-08-17 10:59:50.385371]: Crawling in directory /home/my.dir and outputting in /crawler_output/my-dir-crawl_Aug-17-2016_10-59-50.csv as a csv data store 
WARNING:root:[2016-08-17 11:01:26.500391]: File /home/my.dir/asymlink was not processed because shortcuts and symlinks are not supported 
INFO:root:[2016-08-17 10:59:51.083337]: File crawl is finished 
```

# Known issues and future improvements

## Known Windows Issue With Mounted Filesystems
The Windows implementations of getting usernames, "UIDs", and "GIDs" is imperfect because you do not get a complete picture of file permissions if a mounted filesystem doesn't support security descriptors. For example, some mounted SAMBA shares or VirtualBox's shared folders may not be supported. If a file descriptor cannot be loaded, then it defaults to "Everyone". Link to issue: http://support.microsoft.com/kb/243330

## Different Types of Data Stores
Currently, the script only supports CSV data stores. SQLite is planned to be built in later versions.

## Symbolic Links and Shortcuts
Symbolic links and shortcuts (".lnk" files in Windows) are known to cause problems when you ask about their metadata (file size, whether or not the path exists, etc.) due to the operating system throwing an error when there are too many levels of symbolic links. Thus, these problems *are attempted to be processed*, but their size will not be recorded. If any errors are thrown during the processing of these files, processing will be aborted and the file will be logged. Note that ".lnk" files can ONLY be properly processed on Windows machines, as Linux machines have no easy way of getting information like its target.


-------------------------------------------------------------------------------

** Script Author:** Angela Gross