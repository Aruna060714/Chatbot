TinyTalk AI is a smart product assistant web app built with Flask, OpenSearch, and TinyLLaMA (via LM Studio). It allows users to ask natural language questions and get precise product recommendations with title, image url, prices, and descriptions.

## Features
    1.AI Chatbot using TinyLLaMA via LM Studio
    2.Smart product search powered by OpenSearch 
    3.Fallback to local JSON data when OpenSearch has no matches
    4.Product links displayed in chat UI
    5.Clean and markdown-styled product replies
    6.Easy to run locally without cloud dependencies

## Technologies Used
    -Flask – Python web framework
    -OpenSearch – For product indexing and similarity search
    -LM Studio – Local LLM API using tinyllama-1.1b-chat-v1.0
    -HTML + TailwindCSS – Clean and modern frontend
    -JSON – Local backup product data

## Install Requirements
pip install flask opensearch-py requests

## Run LM Studio
    -Open LM Studio
    -Load the model: TinyLlama-1.1B-Chat-v1.0-GGUF
    -Start the server (ensure it's running at http://127.0.0.1:1234)