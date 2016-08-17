from arguments import Arguments
from crawler import Crawler
from datastore_factory import DataStoreFactory
from datetime import datetime
import logging

def main():
    """The main method of the file crawler program.

    This will:
    - Parse arguments (see arguments.py)
    - Create a data store to store collected file metadata (See datastore*.py)
    - Create and kick off a file crawler that will gather file metadata and save it into the created data store
    - Log errors that occurred while crawling OR finalizing the data store
    """

    # Parse and collect all arguments
    scriptArgs = Arguments()

    # Create and initialize a data store
    dataStore = DataStoreFactory.create(scriptArgs.dataStoreType, scriptArgs.outputDir, scriptArgs.outputFileName)
    dataStore.create_output_dir()
    dataStore.initialize()

    # Create logger; put it in the same path as the output
    logging.basicConfig(filename=dataStore.outputpath(addExt=False) + '.log', level=logging.DEBUG)
    logging.info("[%s]: Crawling in directory %s and outputting in %s as a %s data store" %
    (
        str(datetime.now()),
        scriptArgs.inputDir,
        dataStore.outputpath(),
        scriptArgs.dataStoreType.name)
    )

    try:
        # Create a file crawler and begin crawling
        fileCrawler = Crawler(scriptArgs.inputDir, dataStore)
        fileCrawler.crawl()

        # Finalize the data store
        dataStore.finalize()
    except Exception as ex:
        logging.error("[%s]: %s" % (str(datetime.now()), ex))

    # Log that the crawl is finished
    logging.info("[%s]: File crawl is finished" % str(datetime.now()))

if __name__ == '__main__':
    main()
