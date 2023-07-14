# SpeakerDetect
`SpeakerDetect` is an open-source program written in Python for speaker diarization that makes use of the `pyannote.audio` library. 

<p align="center">
 <a href="https://www.youtube.com/watch?v=37R_R82lfwA"><img src="https://img.youtube.com/vi/37R_R82lfwA/0.jpg"></a>
</p>

1. install python 3.9 visit https://www.python.org/downloads/release/python-390/ for download

2. install requirements from requirements.txt file with
```python
python -m pip install -r requirements.txt
```

3. install FFmpeg [here's](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/) how to do it

4. install [CUDA](https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64) (optional but will be faster if you have a [supported GPU](https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64)) 

5. in order to run the SpeakerDetect CMD with administrator permissions for the 1st time to download the pretrained models.

| Arguments     | what does it do | is mandatory | usage |
| --------------| ---- | ------------- | -----------------|
| -f            | runs individual files (needs full path to file) |  yes  | ```python SpeakerDetect.py -f path_to_file1 path_to_file2 -o path_to_json```|
| -d            | runs a directory with files (only supports 1 directory at a time)   | yes |```python SpeakerDetect.py -d path_to_directory -o path_to_json```  |
| -o            | defines the location where the JSON file will be generated (note that you need to include the file name in path and there there cannot be a file with the same name in that location )| yes | ```python SpeakerDetect.py -f path_to_file1 path_to_file2 -o path_to_json```|


# SpeakerDetect4Autopsy

1. make sure that SpeakerDetect is working

2. install Autopsy 4.20 [here](https://www.autopsy.co)

3. open Autopsy with admin permissions

4. move the folder SpeakerDetect4Autopsy, that contains SpeakerDetect4Autopsy and the SpeakerDetect, in Autopsy's python modules folder. The final path should look something like this: ```C:\Users\USER\AppData\Roaming\autopsy\python_modules\SpeakerDetect4Autopsy```

5. after selecting the data source you want to analyze you must run the `File Type Identification` module first

6. finally you can run the 	`SpeakerDetect4Autopsy` module
