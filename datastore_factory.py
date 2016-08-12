from enum import Enum, unique
from csv_datastore import CsvDataStore

@unique
class DataStoreEnum(Enum):
    """A simple enumerator that describes the different types of DataStore objects that can be created
    """
    csv = 0

class DataStoreFactory(object):
    """A simple factory class that holds a static create method that will create a DataStore instance based on the given DataStoreEnum
    """

    @staticmethod
    def create(dataStoreType, outputDir, outputFileName):
        """A static factory method that will create a DataStore instance based on the given DataStoreEnum

        Params:
            dataStoreType (DataStoreEnum): The type of data store to create
            outputDir (str): The directory to store the results. If the directory does not exist, it will be created for you.
            outputFileName (str): The name of the output file. This does not including the extension, as that is chosen by the data store type.

        Returns:
            DataStore: The newly created instance of a DataStore object
        """
        if dataStoreType is DataStoreEnum.csv:
            return CsvDataStore(outputDir, outputFileName)
        else:
            raise ValueError("An invalid DataStoreType, %s, was given to the factory" % dataStoreType.name)