import google.generativeai as genai
import os, json, time, re
from google.generativeai.types.file_types import File
from typing import Tuple, List


# Function to login into the Gemini API using our credentials in the .env file
def authenticateAPI(apiKey) -> None:
    genai.configure(api_key=apiKey)


# Upload local video file to Google File API
def uploadVideo(filePath: str) -> File:
    # Some basic checks
    if not os.path.exists(filePath):
        raise FileNotFoundError(f'The file at path {filePath} does not exist.')
    if not os.path.isfile(filePath):
        raise ValueError(f'The path {filePath} is not a file.')
    
    # API call to upload
    uploadedVideoFile = genai.upload_file(path=filePath)

    # Verify upload is successful
    while uploadedVideoFile.state.name == "PROCESSING":
        time.sleep(1)
        uploadedVideoFile = genai.get_file(uploadedVideoFile.name)
    if uploadedVideoFile.state.name == "FAILED":
        raise ValueError(f'Uploaded video exited upload with state: {uploadedVideoFile.state.name}')
    
    return uploadedVideoFile


# Wrapper to delete a file in the Google File API
def deleteVideo(uploadedVideoFile: File) -> None:
    genai.delete_file(uploadedVideoFile.name)


# Given your video file, prompt the LLM and return the response in a specific format
def modelInference(videoFile: File) -> str:
    prompt = (
        'You are an expert in understanding the contents of a video based on visual features. '
        'You are also an expert at creating social media captions based on the video you see. '
        'Provide two captions for this video; one that is optimized to perform well and go viral on on TikTok, and '
        'the other to do the same on Instagram Reels. Do not include hashtags in the captions. '
        'Provide 10 hashtags that would work well to push this '
        'video to what you beleive would be its target audience is striking a balance between going viral and '
        'providing relevance to the videos content. Of the 10, provide 5 tailored more towards virality, and 5 '
        'tailored more towards relevance. Return the results as a string formatted as '
        '"[{"tiktok": {"caption": caption, "virality": [list of hashatgs], "relevance": [list of hashatgs]}, '
        '"instagram": {"caption":caption, "virality": [list of hashatgs], "relevance": [list of hashatgs]} }]".'
        )
    
    # Model being used -> Gemini 1.5 Flash in this case
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash-latest")
    # API call
    response = model.generate_content([prompt, videoFile], request_options={"timeout": 600}).text
    
    # Verify the response is in the correct format, and if not, prompt the model again. In my testing, incorrect 
    # generation of the desired format has only happened once. But I figured I may as well as include this since the
    # odds of it producing back to back misformats is low
    while not verifyResponse(response):
        response = model.generate_content([prompt, videoFile], request_options={"timeout": 600})

    return response


# Verify the returned string from the model generation is in the expected format as specifici in the prompt
def verifyResponse(response: str) -> bool:
    try:
        content = json.loads(response)[0]

        # Go through the various checks
        for platform in ['tiktok', 'instagram']:
            caption = content.get(platform, {}).get('caption')
            virality = content.get(platform, {}).get('virality')
            relevance = content.get(platform, {}).get('relevance')

            if not isinstance(caption, str):
                raise TypeError('Caption returned is not a string.')

            if not isinstance(virality, list) or not all(isinstance(item, str) for item in virality):
                raise TypeError('Viral hastags returned in an invalid format.')
            
            if not isinstance(relevance, list) or not all(isinstance(item, str) for item in relevance):
                raise TypeError('Relevance hastags returned in an invalid format.')
        
        # If all is well, we return true
        return True
    except TypeError:
        return False


# Fromatting function to parse through the raw response from the model and return a tuple of results
# The 'platform' parameter here specifies whether to extract the TikTok results using "platform = 'tiktok", 
# or the IG results using "platform = 'instagram"
def parseResponse(response: str, platform: str) -> Tuple[str, List[str], List[str]]:
    content = json.loads(response)[0]

    caption = content.get(platform, {}).get('caption')
    caption = re.sub(r'#\w+', '', caption)
    virality = content.get(platform, {}).get('virality')
    relevance = content.get(platform, {}).get('relevance')

    return (caption, virality, relevance)


