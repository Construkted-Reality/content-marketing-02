# The same command, but with an API key

# Replace YOUR_API_KEY with the key you set
# Replace my-model with your served model name

curl http://192.168.8.90:42069/v1/chat/completions \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer outsider" \
  -d '{
    "model": "gpt-oss-120b",
    "messages": [
      {
        "role": "user",
        "content": "summarize the content from https://pmc.ncbi.nlm.nih.gov/articles/PMC11598270/"
      }
    ]
  }'
