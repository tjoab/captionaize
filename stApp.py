import streamlit as st
import tempfile, os, time
from typing import List, Generator
from helper import authenticateAPI, uploadVideo, deleteVideo, modelInference, parseResponse

# Generator to stream processed request data
def streamPostContent(caption: str, viralHashtags: List[str], relevanceHashtags: List[str]) -> Generator[str, None, None]:
    captionMkdw = [ word + ' ' for word in caption.split(" ")]
    viralMkdw = [ ':blue[#'+ hashtag + '] ' for hashtag in viralHashtags]
    relevanceMkdw = [ ':orange[#'+ hashtag + '] ' for hashtag in relevanceHashtags]
    for chunk in captionMkdw + viralMkdw + relevanceMkdw:
        time.sleep(0.08)
        yield chunk


# Generator to stream sentences, i.e. strings seperated by spaces
def streamSentence(sentence: str) -> Generator[str, None, None]:
    for word in sentence.split(" "):
        time.sleep(0.08)
        yield word + " "


# Streaming function to hack markdown text into Streamlit
def writeStream(stream: Generator[str, None, None]) -> None:
    result = ""
    container = st.empty()
    for chunk in stream:
        result += chunk
        container.write(result, unsafe_allow_html=True)


# Log into the Google Gemini API
authenticateAPI(st.secrets['GOOGLE_API_KEY'])

# Streamlit page configs and some CSS style updates
st.set_page_config(page_title="captionaize", page_icon="resources/robot.png",)
st.markdown('''<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>''', unsafe_allow_html=True)

# Into section of Streamlit application
st.image('resources/captionaize.png', use_column_width=True)
st.markdown("Generate TikTok— and Instagram—tailored captions and hashtags for your videos using the power of some super creative robots up in the clouds :cloud: 🤖 💬 :cloud:")
st.divider()

st.subheader('How to use?')
st.markdown("Using the file uploader below, select your video then hit :green-background[:green[run]] ")
st.markdown("Then sit back, relax and enjoy ")
st.markdown(":blue-background[:blue[Note:]] Click the little :red-background[:red[x]] to remove your video, select another one or cancel any ongoing process")
st.markdown("")
st.markdown("**PS** don't do this ⬆️⬆️ if you haven't taken note of your captions/hashtags! Removing the video will also delete your generated content🫣😅")
st.divider()

# Video uploading section
allowedVideoTypes = ["mp4","mpeg","mov","avi","mpg","webm","wmv"]
video = st.file_uploader("Upload your video 🎥 🎞️ :", type = allowedVideoTypes)
if video:
    run = st.button("Run", use_container_width=True)
    st.divider()

    # Execute main pipeline using helper functions 
    if run:
        with st.status("Robots are currently hard at work 🤖 ...", expanded=True) as status:
            st.write("Stealing your video's data 😈 ...")
            
            # Create a temp file for the uploaded video data and write to a file. Sadly, the Gemini File API expects 
            # string filepaths and connot handle bytes data directly, so there writing to a file was a necessity to use the API
            with tempfile.NamedTemporaryFile(delete=False, suffix=video.name) as tempFile:
                tempFile.write(video.getbuffer())
                tempFilePath = tempFile.name
            time.sleep(2)

            # Upload video to the Gemini File API to be used within our prompt
            st.write("Throwing your data up into the cloud :cloud: ...")
            videoFile = uploadVideo(tempFilePath)
            os.remove(tempFilePath)

            # Prompt the model including the video in the prompt 
            st.write("Robot creativity is ensuing 💡✨🧠 ...")
            response = modelInference(videoFile)

            # Delete the uploaded video from the Gemini File API
            deleteVideo(videoFile)
            status.update(label=":green-background[:green[Done!]] No robots were harmed in this process... 👀", state="complete", expanded=False)
        
        # Parse the response we get back from the LLM 
        ct, vt, rt = parseResponse(response, 'tiktok')
        ci, vi, ri = parseResponse(response, 'instagram')

        # Formate and stream the data to the UI
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            st.subheader('Tiktok Tailored', divider='blue')
            writeStream(stream=streamPostContent(ct, vt, rt))
        with col2:
            st.subheader('Instagram Tailored', divider='blue')
            writeStream(stream=streamPostContent(ci, vi, ri))

        sen = ':blue-background[:blue[Note:]] Hashtags shown in :blue[blue] are more viral-esque, while those shown in :orange[orange] are more about relevance and reaching your target audience'
        writeStream(stream=streamSentence(sen))






