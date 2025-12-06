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

#### Python Dependencies

After activating your virtual environment, install the required packages:

```bash
# All platforms (with virtual environment activated)
pip install -r requirements.txt
```

#### Node.js and Mermaid CLI

The application requires Node.js and mermaid-cli to generate graph diagrams as PNG images.

**Option 1: Using Docker (Recommended)**
- Node.js and mermaid-cli are automatically installed in the Docker container
- No manual installation needed

**Option 2: Local Development**

1. **Install Node.js** (if not already installed):
   - Visit [nodejs.org](https://nodejs.org/) and download the LTS version
   - Or use a package manager:
     ```bash
     # macOS (using Homebrew)
     brew install node
     
     # Ubuntu/Debian
     curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
     sudo apt-get install -y nodejs
     ```

2. **Install mermaid-cli globally**:
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   ```

3. **Verify installation**:
   ```bash
   node --version
   npm --version
   mmdc --version
   ```

**Note:** If you don't install mermaid-cli, the graph PNG generation feature will not work, but the rest of the application will function normally.

## Running the Application

### Environment Variables

Create a `.env` file in the root directory with the following variables (you should create it similar to `.env.example` if it exists):

```env
OPENAI_API_KEY=<your_openai_api_key>
TAVILY_API_KEY=<your_tavily_api_key>
LANGCHAIN_API_KEY=<your_langchain_api_key>
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=multiagent-rag-app
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=multiagent_rag
PORT=8080
```

**Note:** `PORT` is optional and defaults to 8080 if not set. This is useful for deployment platforms like Heroku, AWS Elastic Beanstalk, etc.

### Running Locally

Make sure you have:
1. Activated your virtual environment
2. Installed Python dependencies: `pip install -r requirements.txt`
3. Installed Node.js and mermaid-cli (see "Installing Dependencies" section above)
4. Created a `.env` file with the required environment variables
5. MongoDB running (if using local MongoDB)

Then run the application:

```bash
# Using default port 8080
uvicorn src.server:app --host 0.0.0.0 --port 8080 --reload

# Or use PORT from environment variable
PORT=8080 uvicorn src.server:app --host 0.0.0.0 --port $PORT --reload
```

**Access the application:**
- Web UI: http://localhost:8080 (or the port you specified)
- API Docs: http://localhost:8080/docs
- Health Check: http://localhost:8080/health

### Running with Docker

To run the application using Docker Compose:

```bash
docker compose --env-file .env up
```


### Running in AWS Elastic Beanstalk

This application is configured for deployment on AWS Elastic Beanstalk using Docker.

#### Prerequisites

1. **Install EB CLI**:
   ```bash
   pip install awsebcli
   ```

2. **Configure AWS credentials**:
   ```bash
   aws configure
   ```
   Or set environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```
   or set enviroment varibles:
   ```bash 
   eb setenv \
   OPENAI_API_KEY=<your-key> \
   TAVILY_API_KEY=<your-key> \
   .
   .
   .
   ```

#### Initial Setup

1. **Initialize EB application** (if not already done):
   ```bash
   eb init
   ```
   - Select your region (e.g., us-east-1)
   - Choose "Docker running on 64bit Amazon Linux 2023" as the platform
   - Create or select an application name

2. **Create an environment**:
   ```bash
   eb create <environment-name>
   ```
   Example:
   ```bash
   eb create social-assistant-env
   ```

#### Configuration

The application includes EB configuration files in `.ebextensions/`:

- **Health Check**: Configured to use `/health` endpoint
- **Port**: Set to 8080 (EB will automatically inject PORT environment variable)
- **Docker**: Uses Docker platform for deployment

#### Environment Variables

Set environment variables in EB:

**Option 1: Using EB CLI**
```bash
eb setenv OPENAI_API_KEY=your_key \
          TAVILY_API_KEY=your_key \
          MONGODB_URI=your_mongodb_uri \
          MONGODB_DB_NAME=multiagent_rag \
          LANGCHAIN_API_KEY=your_key \
          LANGCHAIN_TRACING_V2=true \
          LANGCHAIN_PROJECT=multiagent-rag-app
```

**Option 2: Using AWS Console**
1. Go to Elastic Beanstalk → Your Environment → Configuration
2. Navigate to Software → Environment properties
3. Add all required environment variables

#### Deploying

1. **Deploy the application**:
   ```bash
   eb deploy
   ```

2. **Check deployment status**:
   ```bash
   eb status
   ```

3. **View logs** (if issues occur):
   ```bash
   eb logs
   ```

4. **Open the application**:
   ```bash
   eb open
   ```

#### Post-Deployment

- **Health Check**: The application exposes a `/health` endpoint that EB uses for health monitoring
- **Graph PNG**: The graph diagram PNG is generated at startup and available at `/get-graph-png`
- **API Docs**: Available at `https://your-app.elasticbeanstalk.com/docs`

#### Troubleshooting

- **502 Bad Gateway**: Check that the health endpoint `/health` is accessible
- **Port Issues**: Ensure PORT environment variable is set (EB sets this automatically)
- **View Logs**: Use `eb logs` to see application logs and errors


### CI/CD to AWS Elastic Beanstalk through GitHub Actions

1. After you finish deploying to AWS Elastic Beanstalk
2. Go to GitHub Actions -> New workflow 
3. Paste this:
```bash
name: Deploy to Elastic Beanstalk (Docker)
   on:
      push:
         branches: - main #or another barnch 
   
   jobs:
      deploy: 
         runs-on: ubuntu-latest 

         steps: 
         - name: Checkout code 
         uses: actions/checkout@v4

         - name: Generate deployment package (zip)
         run: zip -r deploy.zip . -x "*.git*" 
         
         - name: Configure AWS credentials 
         uses: aws-actions/configure-aws-credentials@v4
         with: 
            aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }} 
            aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }} 
            aws-region: us-east-1 # change if needed 
            
            - name: Upload ZIP to S3
            run: | 
               FILE_KEY="multiagent-rag-$(date +%s).zip" 
               echo "FILE_KEY=$FILE_KEY" >> $GITHUB_ENV 
               aws s3 cp deploy.zip s3://${{ secrets.EB_S3_BUCKET }}/$FILE_KEY 
            
            - name: Create new EB Application Version 
            run: | 
               VERSION="v-$(date +%s)" 
               echo "VERSION=$VERSION" >> $GITHUB_ENV 
               
               aws elasticbeanstalk create-application-version \ 
                  --application-name "${{ secrets.EB_APP_NAME }}" \ 
                  --version-label "$VERSION" \ 
                  --source-bundle S3Bucket=${{ secrets.EB_S3_BUCKET }},S3Key=$FILE_KEY
                  
            - name: Deploy to EB environment 
            run: | 
               aws elasticbeanstalk update-environment \ 
               --environment-name "${{ secrets.EB_ENV_NAME }}" \ 
               --version-label "$VERSION"
```
3. Commit & push to GitHub
4. Add GitHub Secrets:
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - EB_APP_NAME
   - EB_ENV_NAME
   - EB_S3_BUCKET


   
## Testing

The project uses `pytest` for testing. Tests are organized in the `tests/` directory with separate subdirectories for different test types.

### Prerequisites

Make sure you have:
1. Activated your virtual environment
2. Installed all dependencies: `pip install -r requirements.txt`
3. Set up your `.env` file with test API keys (if needed for integration tests)

### Running Tests

#### Run All Tests

To run all tests in the project:

```bash
pytest
```

#### Run Tests with Verbose Output

For more detailed output:

```bash
pytest -v
```

Or for even more verbose output:

```bash
pytest -vv
```

#### Run Specific Test Categories

**Run all service tests:**
```bash
pytest tests/services/
```

#### Run Specific Test Files

To run a specific test file:

```bash
pytest tests/services/test_tavily_service.py
```

#### Test Configuration

The test configuration is defined in `pytest.ini`:
- Test paths: `tests/`
- Python path: `.` (project root)
- Test file pattern: `test_*.py`
- Test class pattern: `Test*`
- Test function pattern: `test_*`
- Default options: `-v --tb=short` (verbose output, short traceback format)
