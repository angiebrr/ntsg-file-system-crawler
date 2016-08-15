from abc import ABCMeta, abstractmethod
import os, errno

class DataStore(metaclass=ABCMeta):
    """An abstract base class that helps storing file metadata row by row.

    This hierarchy was established so it would be simple to add other ways of storing information such as csv, sqlite, json, etc. This way
    only the enumeration and the factory need to be changed instead of having to also change other classes that use the data store.

    Attributes:
        outputDir (str): The directory to store the results. If the directory does not exist, it will be created for you.
        outputFileName (str): The name of the output file. This does not including the extension, as that is chosen by the data store type.
        outputFileExt (str): The extension of the output file. This needs to be overwritten by the child data store AFTER the super's init.
    """
    def __init__(self, outputDir, outputFileName):
        self.outputDir = outputDir
        self.outputFileName = outputFileName
        self.outputFileExt = ''

    def create_output_dir(self):
        """Creates the output directory if it doesn't already exist
        """
        try:
            os.makedirs(self.outputDir)
        except OSError as exception:
            if exception.errno != errno.EEXIST: raise

    def outputpath(self):
        """Returns the path of the data store output.

        Note that this path may or may not be absolute. This depends on whether or not the user gives the absolute/relative path of the output
        directory.

        Returns:
            str: The path of the data store output.
        """
        return self.outputDir + '/' + self.outputFileName + self.outputFileExt

    @abstractmethod
    def initialize(self): 
        """Initializes the data store before any insertions have been made.
        """
        pass

    @abstractmethod
    def finalize(self):
        """Finalizes the data store after all insertions have been made.
        """
        pass

    @abstractmethod
    def insert(self, fullFileParentPath, fileName, fileExt, fileSize, fileOwnerUsername, fileUID, fileGID, fileCTime, fileATime, fileMTime, currOS):
        """Inserts a row into the data store.
        
        Params:
            fullFileParentPath (str): The full (absolute) path of the file's parent directory
            fileName (str): The file's name
            fileExt (str): The file's extension
            fileSize (str): The size of the file
            fileOwnerUsername (str): The file owner's username
            fileUID (str): The file's UID
            fileGID (str): The file's GID
            fileCTime (str): A datetime formatted timestamp string of the ctime
            fileATime (str): A datetime formatted timestamp string of the last accessed time
            fileMTime (str): A datetime formatted timestamp string of the last modified time
            currOS (str): The operating system that is performing the crawl
        """
        pass
