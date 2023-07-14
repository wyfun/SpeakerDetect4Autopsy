to make SpeakerDetect work you need:

1º
install:	python V3.9

2º
install:	requirements from requirements.txt

		example: python -m pip install -r requirements.txt

3º install FFMPEG
here is the link with how to do it: 
		https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/

4º CUDA (optional but will help speed up the process a lot) download link:
	
		https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64

5º in order to run the SpeakerDetect you nead to open the CMD as administrator and write :

Mandatory arguments: 
	--------------------------------------------------------------------------------------------------------------------
	-f --> The application runs using individual files accepting 1 file or several, requiring the full path for each file.
	or
	-d --> The application runs using a directory with files requiring the path to the directory
	----------------------------------------------------------------------------------------------------------------------
	-o --> Defines the path to the generated JSON file
	

python SpeakerDetect.py -d "PATH TO FILE" -o "PATH AND THE FILE NAME of the file where it will be saved"

Example:
 python SpeakerDetect.py -d C:\Users\NAME\Desktop\FileToAnalyse -o C:\Users\NAME\Desktop

OR

 python SpeakerDetect.py -f C:\Users\NAME\Desktop\FileToAnalyse\audio.mp3 -o C:\Users\NAME\Desktop	

-------------------------------------------------------------------------------------------------------------------------


to make SpeakerDetect4Autopsy.py module to work you need:

1ºinstall all the things above to make SpeakerDetect work

2ºinstall autopsy 4.20   link: https://www.autopsy.com

3º open autopsy with admin permissions

4ºput the folder SpeakerDetect4Autopsy, that contains SpeakerDetect4Autopsy and the SpeakerDetect, in Autopsy's module folder. 
The final path will be something like this -> ex:C:\Users\USER\AppData\Roaming\autopsy\python_modules\SpeakerDetect4Autopsy

4º run the File Type Identification module first on the data that you want to analyze

5º run the  module in some data that you have

