# Captionaize 🤖

#### A generative AI tool that uses Google Gemini 1.5 to parse through your videos — suggesting captions and hashtags that are tailored to your content  
The tool suggest different captions/hanstags for TikTok or Instagram, since trends vary on either platform

## How to Use - App
There is a nice UI that you can use to interact with the tool [here](https://captionaize.streamlit.app/)

Upload your video file and away you go

## How to Use - Code
Alternatively, the app can be run by cloning this repo and working with it locally

- Clone repo
  ```python
  git clone https://github.com/tjoab/captionaize.git
  cd captionaize
  ```
- Set up your virtual enviroment using Python 3.11
  ```python
  python3 -m venv venv
  source venv/bin/activate
  ```
- Install dependencies `pip3 install -r requirements.txt`
  
  (Streamlit dependency not needed if you don't plan on running the streamlit app locally - can be removed)
- Create a new main script file
- Import the `helper.py` module to your main script
- Add the following to your main script

  ```python
  from helper import authenticateAPI, uploadVideo, modelInference, deleteVideo
  
  authenticateAPI(YOUR_GOOGLE_API_KEY)

  filePath = "path_to_your_video_file_in_project_dir"
  
  videoFile = uploadVideo(filePath)
  
  response = modelInference(videoFile)
  
  deleteVideo(videoFile)
  ```

- The `response` variable contains the raw response from the LLM request, which can be printed directly and inspected, but it is a bit ugly.
  You could also import the `parseResponse()` function from the `helper` module and get a formatted tuple:
  
  `Tuple[str, List[str], List[str]] = (Caption, List of Viral-esque Hashtags, List of Relevance-esque Hastags)`
  ```python
  from helper import parseResponse

  platform = "tiktok"
  # or
  platform = "instagram"
  
  parseResponse(response, platform)
  
  ```

## 🛠️ Built With

  - [Google Gemini 1.5 Flash](https://deepmind.google/technologies/gemini/flash) - The LLM used
  - [Streamlit](https://streamlit.io/) - The UI library used - hosting also done on their servers
 
## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## ☕ Support

If you find this project helpful, you can support me by buying a coffee:

[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee--yellow.svg?style=social&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/tjoab)

