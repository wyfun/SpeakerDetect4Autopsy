import jarray
import inspect
from java.lang import System
from java.util.logging import Level
from org.sleuthkit.datamodel import SleuthkitCase
from org.sleuthkit.datamodel import AbstractFile
from org.sleuthkit.datamodel import ReadContentInputStream
from org.sleuthkit.datamodel import BlackboardArtifact
from org.sleuthkit.datamodel import BlackboardAttribute
from org.sleuthkit.datamodel import TskData
from org.sleuthkit.autopsy.ingest import IngestModule
from org.sleuthkit.autopsy.ingest.IngestModule import IngestModuleException
from org.sleuthkit.autopsy.ingest import DataSourceIngestModule
from org.sleuthkit.autopsy.ingest import FileIngestModule
from org.sleuthkit.autopsy.ingest import IngestModuleFactoryAdapter
from org.sleuthkit.autopsy.ingest import IngestMessage
from org.sleuthkit.autopsy.ingest import IngestServices
from org.sleuthkit.autopsy.ingest import ModuleDataEvent
from org.sleuthkit.autopsy.coreutils import Logger
from org.sleuthkit.autopsy.casemodule import Case
from org.sleuthkit.autopsy.casemodule.services import Services
from org.sleuthkit.autopsy.casemodule.services import FileManager
from org.sleuthkit.autopsy.casemodule.services import Blackboard
from org.sleuthkit.datamodel import Score
from java.util import Arrays
from org.sleuthkit.autopsy.datamodel import ContentUtils
from java.io import File
from java.util import ArrayList

from datetime import date
import json

#jython
import subprocess
import os
import threading
import sys
import time
import shutil
import glob




def copyToTempFile(file):
        root, ext = os.path.splitext(file.getName())
        tmpFilename =  root + "-" + str(file.getId()) + ext
        tempDir = Case.getCurrentCase().getTempDirectory()
        tmpPath = os.path.join(tempDir, tmpFilename)
        ContentUtils.writeToFile(file, File(tmpPath))
        return tmpPath

class SampleJythonDataSourceIngestModuleFactory(IngestModuleFactoryAdapter):
    moduleName = "SpeakerDetect4Autopsy"

    def getModuleDisplayName(self):
        return self.moduleName

    def getModuleDescription(self):
        return "This module was created with the aim of enabling the automatic identification and grouping of speech segments in audio recordings. Its main function is to recognize and distinguish one or more speakers in different audio/video files."

    def getModuleVersionNumber(self):
        return "1.0"

    def isDataSourceIngestModuleFactory(self):
        return True

    def createDataSourceIngestModule(self, ingestOptions):
        return SampleJythonDataSourceIngestModule()


class SampleJythonDataSourceIngestModule(DataSourceIngestModule):
    _logger = Logger.getLogger(SampleJythonDataSourceIngestModuleFactory.moduleName)

    def log(self, level, msg):
        self._logger.logp(level, self.__class__.__name__, inspect.stack()[1][3], msg)

    def __init__(self):
        self.context = None

    def startUp(self, context):
        self.context = context

    def process(self, dataSource, progressBar):
        progressBar.switchToIndeterminate()
        blackboard = Case.getCurrentCase().getSleuthkitCase().getBlackboard()
        fileManager = Case.getCurrentCase().getServices().getFileManager()
        files = fileManager.findFiles(dataSource, "%")

        
        fileCount = 0
        len_files = 0


        # Create new artifact
        exif_vides_art_type = blackboard.getOrAddArtifactType("BY_FILE", "byFile")
        
        # Create new attribute
        file_path_att_type = blackboard.getOrAddAttributeType('FILE_PATH',BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "File Path")
        speaker_att_type = blackboard.getOrAddAttributeType('SPEAKER',BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "Speaker ID")
        start_time_attt_type = blackboard.getOrAddAttributeType('START_TIME',BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DOUBLE, "Start Time")
        end_time_att_type = blackboard.getOrAddAttributeType('END_TIME',BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DOUBLE, "End Time")
        duration_time_att_type = blackboard.getOrAddAttributeType('DURATION_TIME',BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.DOUBLE, "DurationTime")
        hms_time_att_type = blackboard.getOrAddAttributeType('HMS_TIME',BlackboardAttribute.TSK_BLACKBOARD_ATTRIBUTE_VALUE_TYPE.STRING, "h : m : s")

        for file in files:
                if ((file.getMIMEType() is not None) and (file.getMIMEType().startswith("video") or file.getMIMEType().startswith("audio"))): 
                    tmpFile = copyToTempFile(file)
                    len_files += 1
                    self.log(Level.INFO, "FILENAME " + str(file.getName()))


        numFiles = int(len_files)
        self.log(Level.INFO, "found " + str(numFiles) + " files")
        progressBar.switchToDeterminate(numFiles)


        path_project = os.path.expanduser("~")+'\AppData\Roaming\\autopsy\python_modules\SpeakerDetect4Autopsy\SpeakerDetect.py'
        path_python="python.exe"
        directory_path= os.path.dirname(tmpFile)
        path_json = os.path.dirname(tmpFile)+"\\audioTime.json"
        command=[path_python,path_project ,"-d",directory_path,"-o",path_json]
        self.log(Level.INFO, str(command))
        process = subprocess.Popen(command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Wait for the process to finish and capture the output
        stdout, stderr = process.communicate()
        # Decode the output from bytes to string
        stdout = stdout.decode('utf-8')
        stderr = stderr.decode('utf-8')
        # Check the return code
        returncode = process.returncode
        if returncode == 0:
            self.log(Level.INFO, "DEU"+ stdout)
        else:
            self.log(Level.INFO, "NAODEU"+ stderr)
        time.sleep(2)
        
        if path_json:
            with open(path_json) as f:
                data = json.load(f) 
            by_file_data = data['byFile']
        else:
            self.log(Level.INFO, "JSON FILE ERROR")
 


        for file in files:
            if ((file.getMIMEType() is not None) and (file.getMIMEType().startswith("video") or file.getMIMEType().startswith("audio"))):
                # Check if the user pressed cancel while we were busy
                if self.context.isJobCancelled():
                    return IngestModule.ProcessResult.OK

                self.log(Level.INFO, "Processing file: " + file.getName())
                fileCount += 1

                for filename, speaker_data in by_file_data.items():
                    if str(os.path.splitext(file.name)[0].lower()) == str(filename.split('-')[0].lower()):
                        for speaker, segments in speaker_data.items():
                            for segment in segments:

                                art = file.newArtifact(exif_vides_art_type.getTypeID ())
                                attributes = ArrayList()

                                attributes.add(BlackboardAttribute(file_path_att_type, SampleJythonDataSourceIngestModuleFactory.moduleName, str(tmpFile)))
                                attributes.add(BlackboardAttribute(speaker_att_type, SampleJythonDataSourceIngestModuleFactory.moduleName, str(speaker.split("_")[1])))
                                attributes.add(BlackboardAttribute(start_time_attt_type, SampleJythonDataSourceIngestModuleFactory.moduleName, round(float(segment['start']),3))) 
                                attributes.add(BlackboardAttribute(end_time_att_type, SampleJythonDataSourceIngestModuleFactory.moduleName, round(float(segment['end']),3)))
                                attributes.add(BlackboardAttribute(duration_time_att_type, SampleJythonDataSourceIngestModuleFactory.moduleName, round(float(segment['duration']),3)))

                                hours = int(float(segment['start']) / 3600)
                                minutes = int((float(segment['start']) - (hours * 3600)) / 60)
                                seconds = int(float(segment['start']) - (hours * 3600) - (minutes * 60))
                                converted_time = "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))
                                converted_time_str = str(converted_time)
                                attributes.add(BlackboardAttribute(hms_time_att_type, SampleJythonDataSourceIngestModuleFactory.moduleName, str(converted_time_str)))
                                try:
                                    art.addAttributes(attributes)
                                except:
                                    self.log(Level.INFO, "attribute Error ->>> Error adding attribute to artifact")
           
                                try:
                                    blackboard.postArtifact(art, SampleJythonDataSourceIngestModuleFactory.moduleName, self.context.getJobId())
                                except Blackboard.BlackboardException as e:
                                    self.log(Level.SEVERE, "Error indexing artifact " + art.getDisplayName())
                    else:
                        continue


                        # To further the example, this code will read the contents of the file and count the number of bytes
                        inputStream = ReadContentInputStream(file)
                        buffer = jarray.zeros(1024, "b")
                        totLen = 0
                        readLen = inputStream.read(buffer)
                        while (readLen != -1):
                            totLen = totLen + readLen
                            readLen = inputStream.read(buffer)

                # Update the progress bar
                progressBar.progress(fileCount)
                self.log(Level.INFO, "files caunt ->" + str(fileCount))

            #Post a message to the ingest messages in box.
            message = IngestMessage.createMessage(IngestMessage.MessageType.DATA,
                "Sample Jython Data Source Ingest Module", "Found %d files" % fileCount)
            IngestServices.getInstance().postMessage(message)


        #Just deleting all audio and video files
        for filename in os.listdir(directory_path):
            if filename.endswith('.json'):
                continue  # Skip .json files
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)


        return IngestModule.ProcessResult.OK