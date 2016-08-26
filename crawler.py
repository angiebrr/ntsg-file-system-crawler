import os, sys, time, logging, utilities as util
from datetime import datetime
from tqdm import tqdm

# ---------------------------------------------------------------------------------------------------------------------------------------
# Import file path libraries depending on the operating system; only windows and linux are supported
# ---------------------------------------------------------------------------------------------------------------------------------------
osObj = sys.platform.lower()
from pathlib import Path
if osObj.startswith('win'):
    import win32security, win32com.client
    currOS = 'windows'
elif osObj.startswith('linux'):
    import subprocess
    currOS = 'linux'
else:
    raise RuntimeError('The current operating system is not supported for file crawling.')

class Crawler(object):
    """Using the given input directory and data store, this crawls the directory recursively for files and saves their metadata.

    This class has implemented different methods for get_file_owner_username and get_file_uid_gid for Windows and Linux machines since
    retrieval of this metadata is different for the two systems.

    Libraries are selectively imported based on operating system. As of now, only Windows and Linux are supported.

    NOTE: Files that are symbolic links OR shortcut files (i.e. extensions with .lnk) will NOT be processed because of errors that can
    arise when trying to gather stats about them

    Attributes:
        inputDir (str): The directory that will be crawled through
        dataStore (DataStore): DataStore object that helps storing file metadata row by row
    """
    def __init__(self, inputDir, dataStore):
        self.inputDir = inputDir
        self.dataStore = dataStore



    def crawl(self):
        """Using the given input directory and data store, this crawls the directory recursively for files/directories and saves their metadata.
        """

        inputPathData = Path(self.inputDir)
        processedDirs = set()
        pbarDesc = "Processing file %s"
        pbarDirDesc = "Processing directory %s"
        pbarDescSleeping = "Sleeping while processing file %s"
        k = 0
        d = 0
        with tqdm( desc=(pbarDesc % k) ) as progressBar:
            # insert rows for file information
            for path, dirs, files in os.walk(self.inputDir):
                for name in files:
                    # update progress bar
                    progressBar.set_description(pbarDesc % k)
                    progressBar.update(1)
                    try:
                        # get basic file information from path object and do not process it if it fails
                        decodedPath = path.encode('utf-8', 'surrogateescape').decode('ISO-8859-1')
                        decodedName = name.encode('utf-8', 'surrogateescape').decode('ISO-8859-1')
                        fullPath = os.path.join(decodedPath, decodedName)
                        pathData = Path(fullPath)
                        fileExt = pathData.suffix
                        fileMode =  'FILE' if not pathData.is_symlink() and not fileExt.lower() == '.lnk' else 'LINK'

                        if pathData.exists():
                            try:
                                # gather file info
                                fullFileParentPath = pathData.parents[0]
                                fileRealPath = self.get_file_real_path(fullPath, fileMode, fileExt)
                                fileName = pathData.stem
                                fileOwnerUsername = self.get_file_owner_username(pathData)
                                fileUID, fileGID =  self.get_file_uid_gid(fullPath)
                                fileCTime, fileATime, fileMTime = self.get_file_datetimes(fullPath)
                                fileSize = self.get_file_size(fullPath) if fileMode != 'LINK' else 0

                                # insert it into a data store
                                self.dataStore.insert(fileMode, fullFileParentPath, fileName, fileExt, fileSize, fileOwnerUsername, fileUID, fileGID,
                                                      fileCTime, fileATime, fileMTime, fileRealPath, currOS)

                                # update all parent directories with file size
                                for parentPath in pathData.parents:
                                    if parentPath in inputPathData.parents:# do not update/insert directories that we aren't crawling into (i.e. parents of input dir)
                                        break
                                    elif parentPath not in processedDirs:
                                        # update progress bar
                                        progressBar.set_description(pbarDirDesc % d)
                                        progressBar.update(1)
                                        d += 1
                                        # only process a directory once
                                        processedDirs.add(parentPath)
                                        self.process_directory(parentPath)

                            except Exception as ex:
                                logging.error("[%s]: Problem processing file %s \r\n %s" % ( str(datetime.now()), fullPath, util.get_formatted_exception() ))
                    except Exception as ex:
                        logging.error("[%s]: Problem pre-processing a file \r\n %s" % ( str(datetime.now()), util.get_formatted_exception() ))

                    # sleep for 3 seconds every 10000 files so the I/O bus doesn't lock up
                    if k+d >= 10000 and  k+d % 10000 == 0:
                        progressBar.set_description(pbarDescSleeping % k)
                        progressBar.update(1)
                        time.sleep(3)
                    k += 1

            # finalize the data store
            self.dataStore.finalize()

    def process_directory(self, pathData):
        """Processes a directory and adds it to the data store.

        Params:
            pathData (Path): The Path object of the file
        """

        dirPath = str(pathData)
        try:
            # gather directory info
            fileMode = 'DIR'
            fileName = pathData.stem
            fileExt = ''
            fileRealPath = ''
            fileOwnerUsername = self.get_file_owner_username(pathData)
            fileUID, fileGID = self.get_file_uid_gid(dirPath)
            fileCTime, fileATime, fileMTime = self.get_file_datetimes(dirPath)
            dirSize = self.get_dir_size(dirPath)

            # insert it into the data store
            self.dataStore.insert(fileMode, dirPath, fileName, fileExt, dirSize, fileOwnerUsername, fileUID, fileGID,
                                  fileCTime, fileATime, fileMTime, fileRealPath, currOS)
        except Exception as ex:
            logging.error("[%s]: Problem processing directory %s \r\n %s" % ( str(datetime.now()), dirPath, util.get_formatted_exception() ))

    def get_file_size(self, fullPath):
        """Returns the size of the file.

        If there are too many levels of symbolic links, this may throw an exception. The file size returned will just be '-1'

        Params:
            fullPath (str): The full path of the file

        Returns:
            str: A string of the file size.

        """
        try:
            fileStatData = os.stat(fullPath)
            fileSize = fileStatData.st_size

            return str(fileSize)
        except Exception as ex:
            logging.error("[%s]: Problem processing file %s \r\n %s" % ( str(datetime.now()), fullPath, util.get_formatted_exception() ))
            return '-1'


    def get_file_datetimes(self, fullPath):
        """Returns the ctime, last accessed time, and the last modified time of the file at the given path.

        The "ctime" is different depending on operating system we are on. On Linux, ctime is the last time the file inode was modified. On
        Windows, ctime is the creation time.

        Params:
            fullPath (str): The full path of the file

        Returns:
            str: A datetime formatted timestamp string of the ctime
            str: A datetime formatted timestamp string of the last accessed time
            str: A datetime formatted timestamp string of the last modified time
        """
        try:
            fileStatData = os.stat(fullPath)
            cDateTime = datetime.fromtimestamp(fileStatData.st_ctime)
            accessedDateTime = datetime.fromtimestamp(fileStatData.st_atime)
            modifiedDateTime = datetime.fromtimestamp(fileStatData.st_mtime)

            return cDateTime, accessedDateTime, modifiedDateTime
        except Exception as ex:
            logging.error("[%s]: Problem processing file %s \r\n %s" % ( str(datetime.now()), fullPath, util.get_formatted_exception() ))
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

            Params:
                pathData (Path): The Path object of the file

            Returns:
                str: The username of the owner of the file.
            """

            fullPath = str(pathData)
            try:
                fileSecurityData = win32security.GetFileSecurity(fullPath, win32security.OWNER_SECURITY_INFORMATION)
                (username, domain, sid_name_use) =  win32security.LookupAccountSid(None, fileSecurityData.GetSecurityDescriptorOwner())

                return username
            except Exception as ex:
                logging.error("[%s]: Problem processing file %s \r\n %s" % ( str(datetime.now()), fullPath, util.get_formatted_exception() ))
                return None

        def get_file_uid_gid(self, fullPath):
            """Returns the uid of the owner of the file and the gid of the primary group owner of the file.

            In Windows, this value will be a lengthy string called a "security descriptor". The primary group SID is hardly used in
            Windows, but it will serve its purpose for the metadata gathering that needs to be done here.

            Params:
                fullPath (str): The full path of the file

            Returns:
                str: The security descriptor (UID) of the owner of the file. None is returned if the file does not exist
                str: The security descriptor (GID) of the primary group owner of the file. None is returned if the file does not exist
            """

            try:
                fileSecurityData = win32security.GetFileSecurity(fullPath, win32security.OWNER_SECURITY_INFORMATION)
                sidUser = fileSecurityData.GetSecurityDescriptorOwner()
                fileSecurityData = win32security.GetFileSecurity(fullPath, win32security.GROUP_SECURITY_INFORMATION)
                sidGroup = fileSecurityData.GetSecurityDescriptorGroup()

                return win32security.ConvertSidToStringSid(sidUser), win32security.ConvertSidToStringSid(sidGroup)
            except Exception as ex:
                logging.error("[%s]: Problem processing file %s \r\n %s" % ( str(datetime.now()), fullPath, util.get_formatted_exception() ))
                return None, None

        def get_file_real_path(self, fullPath, fileMode, fileExt):
            """Returns the "real path" of the file.

            If it's a shortcut (.lnk file), it will return the true path that it's pointing to. If it's not a shortcut, then it will just return an empty string. If something goes
            wrong, then an empty string is also returned.

            Params:
                fullPath (str): The full path of the file
                fileMode (str): The mode of the file
                fileExt (str): The extension of the file

            Returns:
                str: A string of the "real path" of the file.

            """

            try:
                if fileExt.lower() == '.lnk' and fileMode == 'LINK':
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(fullPath)
                    realPath = shortcut.Targetpath

                    return realPath
                else:
                    return ''
            except Exception as ex:
                logging.error("[%s]: Problem processing file %s \r\n %s" % ( str(datetime.now()), fullPath, util.get_formatted_exception() ))
                return ''

        def get_dir_size(self, fullPath):
            """Retrieves the size of the directory.

            Note that, for unknown reasons, sometimes this throws an error and won't give you the size. If that ever happens, -1 is returned. This happened when I ever asked for the
            "Documents" folder size, but I have no idea why.

            Params:
                fullPath (str): The full path of the directory

            Returns:
                str: A string of the total size of the directory. If something goes wrong, '-1' is returned.
            """

            try:
                fileSystemObject = win32com.client.Dispatch("Scripting.FileSystemObject")
                folderObject = fileSystemObject.GetFolder(fullPath)
                dirSize = folderObject.Size

                return dirSize
            except Exception as ex:
                logging.error("[%s]: Problem processing directory %s \r\n %s" % ( str(datetime.now()), fullPath, util.get_formatted_exception() ))
                return '-1'

    # ----------------------------------------------------------------------------------------
    # LINUX implementations of getting usernames, uids, and gids
    # ----------------------------------------------------------------------------------------
    elif osObj.startswith('linux'):

        def get_file_owner_username(self, pathData):
            """Returns the username of the owner of the file

            If the user ID is not native to the operating system, (i.e. a Windows user in a Linux OS) then
            "NonNativeUser" is returned.

            Params:
                pathData (Path): The Path object of the file

            Returns:
                str: The username of the owner of the file.
            """

            try:
                owner = pathData.owner()
            except Exception:
                owner = "NonNativeUser"
            return owner

        def get_file_uid_gid(self, fullPath):
            """Returns the uid of the owner (user) of the file and the gid of the group of the file.

            In Linux, all files have and regularly use the "user" and "group" metadata information

            Params:
                fullPath (str): The full path of the file

            Returns:
                str: The UID of the owner (user) of the file.
                str: The GID of the group of the file.
            """

            try:
                statData = os.stat(fullPath)

                return statData.st_uid, statData.st_gid
            except Exception as ex:
                logging.error("[%s]: Problem processing file %s \r\n %s" % ( str(datetime.now()), fullPath, util.get_formatted_exception() ))
                return None, None

        def get_file_real_path(self, fullPath, fileMode, fileExt):
            """Returns the "real path" of the file.

            If it's a symbolic link, it will return the true path that it's pointing to (even if it's multi-layered). If it's not a symbolic link, then it will just return an empty
            string. If something goes wrong, then an empty string is also returned.

            If it's a shortcut ('.lnk' file), the true path cannot be determined and a string with the problem stated is returned

            Params:
                fullPath (str): The full path of the file
                fileMode (str): The mode of the file
                fileExt (str): The file extension

            Returns:
                str: A string of the "real path" of the file.
            """

            try:
                if fileExt.lower() != '.lnk' and fileMode == 'LINK':
                    realPath = os.path.realpath(fullPath)
                    return realPath
                else:
                    return ''
            except Exception as ex:
                logging.error("[%s]: Problem processing file %s \r\n %s" % ( str(datetime.now()), fullPath, util.get_formatted_exception() ))
                return ''

        def get_dir_size(self, fullPath):
            """Retrieves the size of the directory via "du".

            Params:
                fullPath (str): The full path of the directory

            Returns:
                str: A string of the total size of the directory. If something goes wrong, '-1' is returned.
            """

            try:
                dirSize = subprocess.check_output(['du','-s', fullPath]).split()[0].decode('utf-8')
                return dirSize
            except Exception as ex:
                logging.error("[%s]: Problem processing directory %s \r\n %s" % ( str(datetime.now()), fullPath, util.get_formatted_exception() ))
                return '-1'

    def print_file_information(self, pathData):
        """A debugging method that, given a file Path object, it prints out diagnostic information about the file.

        This includes:
        - Its full path
        - The file owner username
        - The file UID and GID
        - The file CTime, ATime, and MTime
        - A "horizontal rule", or a line of "="

        Params:
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
