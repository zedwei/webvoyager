### Install
1. Install latest version of Python.
2. ```pip install -r requirements.txt``` in the "src" folder. This will install all necessary dependencies of the server code.
3. Add a environment variable called "OPENAI_API_KEY" with the OpenAI API key you're using. Instruction can be found at https://platform.openai.com/docs/quickstart?desktop-os=windows#create-and-export-an-api-key.


### Run
**Option 1:** Start a WebSocket server: 
    ```python .\src\main.py 8765```

**Option 2:** Start a local run with PlayWright simulation:
    ```python .\src\main.py```
