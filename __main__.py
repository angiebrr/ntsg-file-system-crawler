from arguments import Arguments
from crawler import Crawler
from datastore_factory import DataStoreFactory

def main():
    """The main method of the file crawler program.

    This will:
    - Parse arguments (see arguments.py)
    - Create a data store to store collected file metadata (See datastore*.py)
    - Create and kick off a file crawler that will gather file metadata and save it into the created data store
    """

    # Parse and collect all arguments
    scriptArgs = Arguments()

    # Create and initialize a data store
    dataStore = DataStoreFactory.create(scriptArgs.dataStoreType, scriptArgs.outputDir, scriptArgs.outputFileName)
    dataStore.create_output_dir()
    dataStore.initialize()

    # Create a file crawler and begin crawling
    fileCrawler = Crawler(scriptArgs.inputDir, dataStore)
    fileCrawler.crawl()

    # Finalize the data store
    dataStore.finalize()

if __name__ == '__main__':
    main()
