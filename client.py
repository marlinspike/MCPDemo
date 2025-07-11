import os
from dotenv import load_dotenv
from openai import OpenAI

def main():
    # Load Azure settings from .env
    load_dotenv()
    endpoint   = os.getenv("AZURE_OPENAI_ENDPOINT").rstrip("/")  # e.g. https://<your-resource>.openai.azure.com
    api_key    = os.getenv("AZURE_OPENAI_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    # Responses API requires api-version 2025-03-01-preview or later
    api_version = "preview" #os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")

    # Initialize the Next-Gen OpenAI client against the Azure Responses endpoint :contentReference[oaicite:0]{index=0}
    client = OpenAI(
        api_key=api_key,
        base_url=f"{endpoint}/openai/v1/",
        default_query={"api-version": api_version},
    )

    print("Type a prompt (blank to exit):")
    while True:
        prompt = input("You: ").strip()
        if not prompt:
            break

        # Call the stateful Responses API :contentReference[oaicite:1]{index=1}
        resp = client.responses.create(
            model=deployment,
            input=prompt
        )

        # Extract and print the assistant’s reply
        data = resp.model_dump()
        reply = resp.output[0].content[0].text
        print("Model:", reply)

if __name__ == "__main__":
    main()
