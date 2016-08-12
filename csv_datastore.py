from datastore import DataStore
import csv

@DataStore.register
class CsvDataStore(DataStore):
    """A data store class that helps storing file metadata row by row in a CSV file.

    Attributes:
        outputDir (str): The directory to store the results. If the directory does not exist, it will be created for you.
        outputFileName (str): The name of the output file. This does not including the extension, as that is chosen by the data store type.
        outputFileExt (str): The extension of the output file. This needs to be overwritten by the child data store AFTER the super's init.
    """
    def __init__(self, outputDir, outputFileName):
        super(CsvDataStore, self).__init__(outputDir, outputFileName)
        self.outputFileExt = '.csv'


    def initialize(self):
        """Initializes the data store.

        This will create a CSV file and insert the CSV header.
        """
        with open(self.outputpath(), 'w', newline='') as file:
            csvWriter = csv.writer(file)
            csvWriter.writerow \
            ([
                'full_path',
                'file_parent_dir',
                'file_owner_username',
                'file_uid',
                'file_gid',
                'file_ctime',
                'file_accessed_time',
                'file_modified_time',
                'current_os'
            ])


    def insert(self, fullPath, fileParentDir, fileOwnerUsername, fileUID, fileGID, fileCTime, fileATime, fileMTime, currOS):
        """Inserts a row into the data store.

        This will add a comma delimited list of the given arguments

        Params:
            fullPath (str): The full (absolute) path of the file
            fileParentDir (str): The file's parent directory name
            fileOwnerUsername (str): The file owner's username
            fileUID (str): The file's UID
            fileGID (str): The file's GID
            fileCTime (str): A datetime formatted timestamp string of the ctime
            fileATime (str): A datetime formatted timestamp string of the last accessed time
            fileMTime (str): A datetime formatted timestamp string of the last modified time
            currOS (str): The operating system that is performing the crawl
        """
        with open(self.outputpath(), 'a', newline='') as file:
            csvWriter = csv.writer(file)
            csvWriter.writerow \
            ([
                fullPath,
                fileParentDir,
                fileOwnerUsername,
                fileUID,
                fileGID,
                fileCTime,
                fileATime,
                fileMTime,
                currOS
            ])
