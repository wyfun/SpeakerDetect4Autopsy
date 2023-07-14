import time
import torch
import os
from pydub import AudioSegment
import subprocess
import hashlib
from pyannote.audio import Pipeline
import json
import argparse
import tempfile
import re


start = time.time()


parser = argparse.ArgumentParser(description="SpeakerDiarization",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-f", "--file", nargs='+',help="Input full path to file for diarization")
group.add_argument("-d", "--directory", help="Input full directory path with audio files for diarization")
parser.add_argument("-o", "--output", help="name or location of the output file",required=True)

args = parser.parse_args()
config = vars(args)


# Directories and global variables

non_processed_directory = args.directory
processed_directory = tempfile.mkdtemp(prefix='processed')
print(processed_directory)

file_times = []
dration_aux_2 = 0
hash_dict = {}
lst = os.listdir(processed_directory)
number_files = len(lst)
i = 0

if args.output is None:
 json_file = processed_directory+"/other_files/audioTime.json"
else:
 json_file = args.output   


#-----------------------------------------------------------------------------------------
#|                                                                                       |
#|                                      Functions                                        |
#|                                                                                       |
#-----------------------------------------------------------------------------------------

def diarization():
 pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",use_auth_token="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")
 diarization = pipeline(processed_directory+"/other_files/combined_sound.wav")
 with open(processed_directory+"/other_files/audio.rttm", "w") as rttm:
    diarization.write_rttm(rttm)

def write_speakers_json(NameAndTimeOfRTTM):
    with open(json_file, 'r') as f:
        data = json.load(f)


    converted_names_of_files_list=[]
    for i, files in enumerate(NameAndTimeOfRTTM.keys()):
        new_filename = re.sub(r"(-\d+)?_audio\.wav(_silence)?", "", files)
        if i % 2 == 0:
            data['byFile'][new_filename] = {}
            converted_names_of_files_list.append(new_filename)
    print(converted_names_of_files_list)

    with open(json_file, 'w') as f:
        json.dump(data, f) 
    #----------------------------------
    dration_aux_inicio=[0]
    for key,value in NameAndTimeOfRTTM.items():
        dration_aux_inicio.append(value)
    #del dration_aux_inicio[-1]
    print(dration_aux_inicio)

    i = -2
    contador = 0
    for file_names in converted_names_of_files_list:
        f_audio = open(processed_directory+"/other_files/audio.rttm", 'r')
        i= i + 2
        for line in f_audio:
            parts = line.strip().split()
            spkr_id = parts[1]
            start_time = float(parts[3])
            duration = float(parts[4])
            total_time = float(format((float(parts[3])+float(parts[4])), '.3f'))
            speech = (parts[7])

            if start_time <= dration_aux_inicio[i+1]/1000 and total_time >= dration_aux_inicio[i]/1000:
                contador = contador + 1
                if i == 0 :
                    print(str(start_time) + "<="+str(dration_aux_inicio[i+1]/1000) + "  and  " + str(total_time) + ">=" + str(dration_aux_inicio[i]/1000))
                    print("NAME---> "+str(file_names) +"     "  +   "Start time: "+ str(format((start_time-dration_aux_inicio[i]/1000),'.3f')) +"   total_time:   " + str(format(total_time,'.3f'))    + "    duration: "+str(format(duration,'.3f')) + "  SPEAKER---> "+str(speech))
                    print("duration time i:  "+ str(dration_aux_inicio[i]))
                    print(i)
                    print(str(contador) + "\n")

                    speaker_data = {
                        'start': str(format(((start_time-dration_aux_inicio[i]/1000)),'.3f')),
                        'end': str(format(((total_time-dration_aux_inicio[i]/1000)),'.3f')),
                        'duration': duration
                        }
                else:
                    print(str(start_time) + "<="+str(dration_aux_inicio[i+1]/1000) + "  and  " + str(total_time) + ">=" + str(dration_aux_inicio[i]/1000))
                    print("NAME---> "+str(file_names) +"     "  +   "Start time: "+ str(format(((start_time-dration_aux_inicio[i]/1000)-2),'.3f')) +"   total_time:   " + str(format(total_time,'.3f'))    + "    duration: "+str(format(duration,'.3f')) + "  SPEAKER---> "+str(speech))
                    print("duration time i:  "+ str(dration_aux_inicio[i]))
                    print(i)
                    print(str(contador) + "\n")

                    speaker_data = {
                        'start': str(format(((start_time-dration_aux_inicio[i]/1000)-2),'.3f')),
                        'end': str(format(((total_time-dration_aux_inicio[i]/1000)-2),'.3f')),
                        'duration': duration
                        }
                
                if file_names in data['byFile']:
                    if speech in data['byFile'][file_names]:
                        data['byFile'][file_names][speech].append(speaker_data)
                    else:
                        data['byFile'][file_names][speech] = [speaker_data]
                else:
                    data['byFile'][file_names] = {speech: [speaker_data]}

                with open(json_file, 'w') as f:
                    json.dump(data, f)

            else:
                continue

    # #apagar os files que não têm nada           
    # with open(json_file, 'r') as f:
    #     data = json.load(f)

    # # for file_names in converted_names_of_files_list:
    # #     if file_names in data['byFile'] and not data['byFile'][file_names][speech]:
    # #         del data['byFile'][file_names]

#___________________________________________________________________________________________________________________________________________________________________________

    


def write_files_json_concatenate_files():
   # loop to merge the converted files into one
    my_dict = {}
    duration_aux = 0
    
    #counter_silent_2000 = 0
    i = 0
    #print(processed_directory + "-_________________________________________##################################")
    for root, dirs, files in os.walk(processed_directory):
       for file in files:
         #print(file + "-_________________________________________##################################")       
        # get time from file
         result = subprocess.run(["ffmpeg.exe", "-i", processed_directory + "/" + file, "-f", "null", "-"],capture_output=True,text=True)
         #print(str(result) + "-_________________________________________##################################")  
         duration_str = result.stderr.split("Duration: ")[1].split(",")[0]
         hours, minutes, seconds = duration_str.split(":")
         milliseconds = (int(hours) * 3600000+ int(minutes) * 60000+ int(seconds.split(".")[0]) * 1000+ int(seconds.split(".")[1]))
         #1500            0              1500
         milliseconds = duration_aux + milliseconds
         duration_aux = milliseconds
        #print(milliseconds)
         my_dict[file] = milliseconds



         duration_aux = milliseconds + 2000
         my_dict[file+"_silence"] = duration_aux

        # concatenate audio files in one
         file_path = os.path.join(root, file)
         print("FILE  --->" + file_path)
         sound1 = AudioSegment.from_wav(file_path)
         silence = AudioSegment.silent(2000)
         if os.path.exists(os.path.dirname(file_path)+"/other_files/combined_sound.wav"):
             sound3 = AudioSegment.from_wav(os.path.dirname(file_path)+"/other_files/combined_sound.wav")
             combined_sound = sound3  + sound1 + silence 
             combined_sound.export(os.path.dirname(file_path)+"/other_files/combined_sound.wav", format="wav")
         else:
             os.makedirs(os.path.dirname(file_path)+"/other_files")
             combined_sound = sound1 + silence
             combined_sound.export(os.path.dirname(file_path)+"/other_files/combined_sound.wav", format="wav")
         

    #print(my_dict)
    
    return my_dict



if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu") 

print("Using", device ,"device")



#-----------------------------------------------------------------------------------------
#|                                                                                       |
#|                                      File                                             |
#|                                                                                       |
#-----------------------------------------------------------------------------------------

if args.directory is None:
 print("FILE")

 for file in args.file:  
    print(str(file).rsplit("\\",1)[-1])
    if (file.endswith(".mp4") or file.endswith(".mp3") or file.endswith(".3gp") or file.endswith(".ogg") or file.endswith(".webm") or file.endswith(".wmv") or file.endswith(".flv") or file.endswith(".wav")or file.endswith(".m4a")):
         
        with open(file, 'rb') as f:
            hash_value = hashlib.sha256(f.read()).hexdigest()
            if hash_value not in hash_dict.values():
                 hash_dict[file] = hash_value
            else:
                 print(f"Warning: {file} has the same hash value as another file.")
                #print("File -> " + os.path.splitext(file)[0] + " already exists")              
 for file, hash_value in hash_dict.items():
    #print(f"File: {file} | Hash: {hash_value}")
    processed_file = (processed_directory + "/" + str(file).rsplit("\\",1)[-1] + "_audio.wav")
    if os.path.exists(processed_file):
       print("File -> " + os.path.splitext(file)[0] + " already exists")
    else:
       subprocess.call(["ffmpeg","-i",file,"-acodec","pcm_s16le","-ac","1","-ar","16000",processed_file])
       print("File " + processed_file + "created.")

      # loop to merge the converted files into one
 NameAndTimeOfRTTM = write_files_json_concatenate_files()



 diarization()

 data = {
    "byFile": {}
 }
 json_str = json.dumps(data)

 with open(json_file, "w") as f:
    f.write(json_str)


 for key, value in NameAndTimeOfRTTM.items():
    print(f"Key: {key}, Value: {value}")

 write_speakers_json(NameAndTimeOfRTTM)
  

#-----------------------------------------------------------------------------------------
#|                                                                                       |
#|                                      DIRECTORY                                        |
#|                                                                                       |
#-----------------------------------------------------------------------------------------

if args.file is None:
 print("DIRECTORY")
 #Create a Dictionary(name | hash) and then if 2 or more files have the same hash just 1 will be in Dictionary  and the last FOR loop is for convert files to .wav
 for root, dirs, files in os.walk(non_processed_directory):
    for file in files: 
            #print(root)
            #print(dirs)
            #print(files)
            non_processed_file = os.path.join(root, file)
            if (file.endswith(".mp4") or file.endswith(".mp3") or file.endswith(".3gp") or file.endswith(".ogg") or file.endswith(".webm") or file.endswith(".wmv") or file.endswith(".flv")  or file.endswith(".m4a") or file.endswith(".wav")):
                with open(non_processed_file, 'rb') as f:
                 hash_value = hashlib.sha256(f.read()).hexdigest()
                 if hash_value not in hash_dict.values():
                    hash_dict[root+'/'+file] = hash_value
                 else:
                    print(f"Warning: {file} has the same hash value as another file.")
                    #print("File -> " + os.path.splitext(file)[0] + " already exists")
    
 print(hash_dict)


 for file_path, hash_value in hash_dict.items():
    #print(f"File: {file} | Hash: {hash_value}")
    file = os.path.basename(file_path)
    processed_file = (processed_directory + "/" + os.path.splitext(file)[0] + "_audio.wav")
    #print(processed_file)

    #print(processed_file+ "\n\n")
    non_processed_file = file_path
    if os.path.exists(processed_file):
        print("File -> " + os.path.splitext(file)[0] + " already exists")
    else:
        subprocess.call(["ffmpeg","-i",non_processed_file,"-acodec","pcm_s16le","-ac","1","-ar","16000",processed_file,])
        print("File " + processed_file + "created.")


 # loop to merge the converted files into one
 NameAndTimeOfRTTM = write_files_json_concatenate_files()
 #print(file_times)



 diarization()

 data = {
    "byFile": {}
 }

 json_str = json.dumps(data)

 with open(json_file, "w") as f:
    f.write(json_str)



 #for key, value in NameAndTimeOfRTTM.items():
    #print(f"Key: {key}, Value: {value}")

 write_speakers_json(NameAndTimeOfRTTM)
        


#deleting all .wav files
for root, dirs, files in os.walk(processed_directory):
    for file in files:
        if file.endswith('.rttm'):
            continue  # Skip .json files
        file_path = os.path.join(root, file)
        os.remove(file_path)


end = time.time()
print(end - start)


