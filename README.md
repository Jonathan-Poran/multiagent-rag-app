# multiagent-rag-app
A multi-agent system that collaborates to retrieve, process, and synthesize information into structured insights using LangGraph and Tavily (RAG-based)


## Environment Setup

### Setting Up Virtual Environment

Using a virtual environment is highly recommended to isolate project dependencies from your system Python installation.

#### macOS/Linux

1. **Create a virtual environment**:

   ```bash
   python3 -m venv .venv
   ```

2. **Activate the virtual environment**:

   ```bash
   source .venv/bin/activate
   ```

3. **Verify activation** (you should see `(.venv)` in your terminal prompt):

   ```bash
   which python
   # Should output: (.venv) user/.../multiagent-rag-app/.venv/bin/python
   ```

4. **Deactivate when done** (optional):
   ```bash
   deactivate
   ```

#### Windows

##### Using PowerShell

1. **Create a virtual environment**:

   ```powershell
   python -m venv .venv
   ```

2. **Activate the virtual environment**:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. **Verify activation** (you should see `(.venv)` in your prompt):

   ```powershell
   Get-Command python | Select-Object Source
   # Should output: C:\path\multiagent-rag-app\.venv\Scripts\python.exe
   ```

4. **Deactivate when done** (optional):
   ```powershell
   deactivate
   ```


### Installing Dependencies

After activating your virtual environment, install the required packages:

```bash
# All platforms (with virtual environment activated)
pip install -r requirements.txt
```

## Running the Application

### Environment Variables

Create a `.env` file in the root directory with the following variables (you should create it similar to `.env.example` if it exists):

```env
OPENAI_API_KEY=<your_openai_api_key>
LANGCHAIN_API_KEY=<your_langchain_api_key>
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=multiagent-rag-app
```