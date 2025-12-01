# multiagent-rag-app
A RAG-based multi-agent creative assistant that leverages Tavily and OpenAI to retrieve, process, and generate creative content through collaborative agent interactions.


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
TAVILY_API_KEY=<your_tavily_api_key>
LANGCHAIN_API_KEY=<your_langchain_api_key>
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=multiagent-rag-app
```

## Running with Docker

To run the application using Docker Compose:

```bash
docker compose --env-file .env up
```

This will start both the application and MongoDB services. Make sure you have a `.env` file with all required environment variables before running this command.

## Visualizing the Agent Graph

You can visualize the agent workflow graph using [Mermaid Live Editor](https://mermaid.live/edit#pako:eNp1Ul1vgkAQ_CuX7YsmQAH58jS-1J_Qp5bGnLAHJHCQ42hrjf-9B0W0UQk5dm9ndiYTjpDUKQIF0zRjkdSCFxmNBSG8rL-SnEk1dIQknfxESspCIJOxGOCZZE1OXrerP0j_7Hat0qTdbva-bjZTt35uNh9zSikvZKsu8AwFSqZwdi7ml5lEXmKiZuN3fi2CIp0khnoSKNn1_skAMc3NpLa6NUBMSwPGZQ_no5XVjclH9H_jW3ai3bZb5CRFzrpSEV6UJX3iLrc5N_qszRyLLFfUsdw7tCHNgWTWDUsKdaD2HVifybh6z_cBT8CATBYpUCU7NKBCWbG-hWPPjkHlWGEMVJejsxhicdK0hom3uq7OTFl3WQ6Us7LVXdekOqptwfSPcYHoTFC-1J1QQF1_WAH0CN9AvTCwHN_19RuEkbMw4KAhgb70AjdceEvbDyP_ZMDPIGlbXhQtloE-bMeOAs8NTr8Go9Xc). The graph shows the flow between the generation and reflection agents in the multi-agent system.