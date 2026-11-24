# README
# Objective
To build a basic AI agent using langChain

## Video
 https://www.youtube.com/watch?v=fbqavMQYdfw

## Lab
 https://claude.ai/artifact/HRMoT1yyxHcZWm2ZLsvkbR 

## Steps to run:
### Get the Project
``` 
git clone https://github.com/harishagrawal/ai-recruitment-assistant-basic.git
cd ai-recruitment-assistant-basic
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### Configure MODEL and API_KEY
```
cat > .env << 'EOF'
# 1. Choose ONE model, written "provider:model". Keep one MODEL line without "#".
MODEL=groq:openai/gpt-oss-120b
# MODEL=openai:gpt-6-luna
# MODEL=anthropic:claude-sonnet-5-5
# MODEL=google_genai:gemini-flash-latest

# 2. Add the key of that provider only. Never share this file.
GROQ_API_KEY=gsk-your-key-here
# OPENAI_API_KEY=your-key-here
# ANTHROPIC_API_KEY=your-key-here
# GOOGLE_API_KEY=your-key-here
EOF
```

### Run the app
```
# Kill any existing application on port 8501 
kill $(lsof -ti tcp:8501) 2>/dev/null

# runs on default port
streamlit run app.py

# To run on a different port
streamlit run app.py --server.port 8502
```
