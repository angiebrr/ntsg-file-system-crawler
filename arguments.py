from argparse import ArgumentParser, ArgumentTypeError
from datetime import datetime
from datastore_factory import DataStoreEnum

class Arguments(object):
    """Uses ArgumentParser to gather and parse arguments given by the user in the command line.

    Attributes:
        currTime (str): The current time in a datetime formatted string
        argParser (ArgumentParser): An ArgumentParser instance used to gather and parse the given arguments
        inputDir (str): A parsed argument; The directory that will be crawled through
        outputDir (str): A parsed argument; The directory to store the results
        outputFileName (str): A parsed argument; The name of the output file without the extension
        dataStoreType (str): A parsed argument; The type of the output, or i.e. the data store
    """
    def __init__(self):
        # Update the current time
        self.currTime = datetime.now().strftime("%b-%d-%Y_%H-%M-%S")

        # Setup arguments to parse
        self.argParser = ArgumentParser(description='Crawls through a file system gathering metadata about files and outputs its findings.')

        # Required Named arguments
        requiredNamed = self.argParser.add_argument_group('required named arguments')
        requiredNamed.add_argument('-i','--input', type=str, required=True, help='The input directory to crawl through')

        # Optional arguments
        self.argParser.add_argument('-o','--output', type=str, default=self.DEFAULT_OUTPUT_DIR(), help='The directory to store the results. If the directory does not exist, it will be '
                                                                                                       'created for you. (default: "%(default)s") ')
        self.argParser.add_argument('-fn', '--filename', type=self.string_with_format, default=self.DEFAULT_OUTPUT_FILENAME(), help='The name of the output file. This does not including '
                                                                                                                                    'the extension, as that is chosen by the data store '
                                                                                                                                    'type. Please place "%%s" in the name where you want '
                                                                                                                                    'the timestamp to go. (default: "%(default)s") ')
        dataStoreNameList = [enum.name for enum in DataStoreEnum]
        self.argParser.add_argument('-d', '--datastore', choices=dataStoreNameList, default=dataStoreNameList[0], help='The type of the output, or i.e. the data store. (default: "%(default)s") ')

        # Parse all arguments
        args = vars(self.argParser.parse_args())
        self.inputDir = args['input']
        self.outputDir = args['output']
        self.outputFileName = args['filename'] % self.currTime
        self.dataStoreType = DataStoreEnum[args['datastore']]


    def string_with_format(self, string):
        """A "type" function for ArgumentParser to ensure that a "%s" is in the filename string

        Params:
            string (str): The filename (or argument) given from ArgumentParser

        Returns:
            str: The string argument
        """
        if "%s" not in string:
            raise ArgumentTypeError('Please place "%s" in the filename where you want the timestamp to go')
        elif not isinstance(string, str):
            raise ArgumentTypeError('The given argument was not a string')

        return string


    def DEFAULT_OUTPUT_DIR(self):
        """Returns the default constant value of the output directory name.

        By default, this output directory is a relative path.

        Returns:
            str: The default constant value of the output directory name
        """
        return 'output'

    def DEFAULT_OUTPUT_FILENAME(self):
        """Returns the default constant value of the output file name.

        In order to ensure uniqueness between runs.

        Returns:
            str: The default constant value of the output file name.
        """
        return '%s__fsc-output'

