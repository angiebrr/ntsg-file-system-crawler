import os, sys, datetime, time
from tqdm import tqdm

# ---------------------------------------------------------------------------------------------------------------------------------------
# Import file path libraries depending on the operating system; only windows and linux are supported
# ---------------------------------------------------------------------------------------------------------------------------------------
osObj = sys.platform.lower()
from pathlib import Path
if osObj.startswith('win'):
    import win32security
    currOS = 'windows'
elif osObj.startswith('linux'):
    currOS = 'linux'
else:
    raise RuntimeError('The current operating system is not supported for file crawling.')

class Crawler(object):
    """Using the given input directory and data store, this crawls the directory recursively for files and saves their metadata.

    This class has implemented different methods for get_file_owner_username and get_file_uid_gid for Windows and Linux machines since
    retrieval of this metadata is different for the two systems.

    Libraries are selectively imported based on operating system. As of now, only Windows and Linux are supported.

    Attributes:
        inputDir (str): The directory that will be crawled through
        dataStore (DataStore): DataStore object that helps storing file metadata row by row
    """
    def __init__(self, inputDir, dataStore):
        self.inputDir = inputDir
        self.dataStore = dataStore

    def crawl(self):
        """Using the given input directory and data store, this crawls the directory recursively for files and saves their metadata.
        """
        k = 0

        # retrieve all files first in order to use tqdm for progress report
        print("")
        print("Retrieving files for processing...")
        print("")
        osWalkList = list(os.walk(self.inputDir))
        tOSWalkList = tqdm(osWalkList)

        for path, dirs, files in tOSWalkList:
            for name in files:
                # gather file info
                fullPath = os.path.join(path, name)
                pathData = Path(fullPath)
                fullFileParentPath = pathData.parents[0]
                fileName = pathData.stem
                fileExt = pathData.suffix
                fileSize = self.get_file_size(pathData)
                fileOwnerUsername = self.get_file_owner_username(pathData)
                fileUID, fileGID =  self.get_file_uid_gid(pathData)
                fileCTime, fileATime, fileMTime = self.get_file_datetimes(pathData)

                # insert it into a data store
                self.dataStore.insert(fullFileParentPath, fileName, fileExt, fileSize, fileOwnerUsername, fileUID, fileGID, fileCTime, fileATime, fileMTime, currOS)

                # sleep for 5 seconds every 1000 files so the I/O bus doesn't lock up
                if k >= 1000 and  k % 1000 == 0: time.sleep(5)

    def get_file_size(self, pathData):
        """Returns the size of the file

        Args:
            pathData (Path): The Path object of the file

        Returns:
            str: A string of the file size. If it doesn't exist then None is returned

        """

        if pathData.exists():
            fullPath = str(pathData)
            fileStatData = os.stat(fullPath)
            fileSize = fileStatData.st_size

            return str(fileSize)
        else:
            return None


    def get_file_datetimes(self, pathData):
        """Returns the ctime, last accessed time, and the last modified time of the file at the given path.

        The "ctime" is different depending on operating system we are on. On Linux, ctime is the last time the file inode was modified. On
        Windows, ctime is the creation time.

        Args:
            pathData (Path): The Path object of the file

        Returns:
            str: A datetime formatted timestamp string of the ctime
            str: A datetime formatted timestamp string of the last accessed time
            str: A datetime formatted timestamp string of the last modified time
        """

        if pathData.exists():
            fullPath = str(pathData)
            fileStatData = os.stat(fullPath)
            cDateTime = datetime.datetime.fromtimestamp(fileStatData.st_ctime)
            accessedDateTime = datetime.datetime.fromtimestamp(fileStatData.st_atime)
            modifiedDateTime = datetime.datetime.fromtimestamp(fileStatData.st_mtime)

            return cDateTime, accessedDateTime, modifiedDateTime
        else:
            return None, None, None

    # -----------------------------------------------------------------------------------------------------------------------------------
    # WINDOWS implementations of getting usernames, uids, and gids
    #
    # This is imperfect because you do not get a complete picture of file permissions if a mounted filesystem doesn't support security
    # descriptors. For example, some mounted SAMBA shares or VirtualBox's shared folders may not be supported. If a file descriptor
    # cannot be loaded, then it defaults to "Everyone". http://support.microsoft.com/kb/243330
    # -----------------------------------------------------------------------------------------------------------------------------------
    if osObj.startswith('win'):

        def get_file_owner_username(self, pathData):
            """Returns the username of the owner of the file

            Args:
                pathData (Path): The Path object of the file

            Returns:
                str: The username of the owner of the file. None is returned if the file does not exist
            """

            if pathData.exists():
                fullPath = str(pathData)
                fileSecurityData = win32security.GetFileSecurity(fullPath, win32security.OWNER_SECURITY_INFORMATION)
                (username, domain, sid_name_use) =  win32security.LookupAccountSid(None, fileSecurityData.GetSecurityDescriptorOwner())

                return username
            else:
                return None

        def get_file_uid_gid(self, pathData):
            """Returns the uid of the owner of the file and the gid of the primary group owner of the file.

            In Windows, this value will be a lengthy string called a "security descriptor". The primary group SID is hardly used in
            Windows, but it will serve its purpose for the metadata gathering that needs to be done here.

            Args:
                pathData (Path): The Path object of the file

            Returns:
                str: The security descriptor (UID) of the owner of the file. None is returned if the file does not exist
                str: The security descriptor (GID) of the primary group owner of the file. None is returned if the file does not exist
            """

            if pathData.exists():
                fullPath = str(pathData)
                fileSecurityData = win32security.GetFileSecurity(fullPath, win32security.OWNER_SECURITY_INFORMATION)
                sidUser = fileSecurityData.GetSecurityDescriptorOwner()
                fileSecurityData = win32security.GetFileSecurity(fullPath, win32security.GROUP_SECURITY_INFORMATION)
                sidGroup = fileSecurityData.GetSecurityDescriptorGroup()

                return win32security.ConvertSidToStringSid(sidUser), win32security.ConvertSidToStringSid(sidGroup)
            else:
                return None, None

    # ----------------------------------------------------------------------------------------
    # LINUX implementations of getting usernames, uids, and gids
    # ----------------------------------------------------------------------------------------
    elif osObj.startswith('linux'):

        def get_file_owner_username(self, pathData):
            """Returns the username of the owner of the file

            If the user ID is not native to the operating system, (i.e. a Windows user in a Linux OS) then
            "NonNativeUser" is returned.

            Args:
                pathData (Path): The Path object of the file

            Returns:
                str: The username of the owner of the file. None is returned if the file does not exist
            """

            if pathData.exists():
                try:
                    owner = pathData.owner()
                except Exception:
                    owner = "NonNativeUser"
                return owner
            else:
                return None

        def get_file_uid_gid(self, pathData):
            """Returns the uid of the owner (user) of the file and the gid of the group of the file.

            In Linux, all files have and regularly use the "user" and "group" metadata information

            Args:
                pathData (Path): The Path object of the file

            Returns:
                str: The UID of the owner (user) of the file. None is returned if the file does not exist
                str: The GID of the group of the file. None is returned if the file does not exist
            """

            if pathData.exists():
                fullPath = str(pathData)
                statData = os.stat(fullPath)

                return statData.st_uid, statData.st_gid
            else:
                return None, None


    def print_file_information(self, pathData):
        """A debugging method that, given a file Path object, it prints out diagnostic information about the file.

        This includes:
        - Its full path
        - The file owner username
        - The file UID and GID
        - The file CTime, ATime, and MTime
        - A "horizontal rule", or a line of "="

        Args:
            pathData (Path): The Path object of the file
        """

        fileParentDir = pathData.parent.name
        fileName = pathData.name
        fileOwnerUsername = self.get_file_owner_username(pathData)
        fileOwnerUID, fileOwnerGID = self.get_file_uid_gid(pathData)
        fileCTime, fileATime, fileMTime = self.get_file_datetimes(pathData)
        fullPath = str(pathData)
        print("Name: %s" % fileName)
        print("Path: %s" % fullPath)
        print("Parent Dir: %s" % fileParentDir)
        print("Owner: %s" % fileOwnerUsername)
        print("UID: %s | GID: %s" % (fileOwnerUID, fileOwnerGID))
        print("CTime: %s | ATime: %s | MTime: %s" % (fileCTime, fileATime, fileMTime))
        print("====================================================================")
