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

        This will initialize a CSV row list and insert the CSV header to it
        """
        self.csvRows = []
        self.csvRows.append \
        ([
            'full_file_parent_path',
            'file_name',
            'file_ext',
            'file_size',
            'file_owner_username',
            'file_uid',
            'file_gid',
            'file_ctime',
            'file_accessed_time',
            'file_modified_time',
            'current_os'
        ])

    def finalize(self):
        """Finalizes the data store after all data has been inserted.

        Iterates over the CSV row list and writes each row to the output CSV file
        """
        with open(self.outputpath(), 'a', newline='') as csvFile:
            csvWriter = csv.writer(csvFile)
            for row in self.csvRows:
                csvWriter.writerow(row)

    def insert(self, fullFileParentPath, fileName, fileExt, fileSize, fileOwnerUsername, fileUID, fileGID, fileCTime, fileATime, fileMTime, currOS):
        """Inserts a row into the data store.

        This will add a comma delimited list of the given arguments to the CSV rows list

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
        self.csvRows.append \
        ([
            fullFileParentPath,
            fileName,
            fileExt,
            fileSize,
            fileOwnerUsername,
            fileUID,
            fileGID,
            fileCTime,
            fileATime,
            fileMTime,
            currOS
        ])
