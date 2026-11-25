import requests, argparse, os
from rich.markdown import Markdown
from rich.console import Console

parser = argparse.ArgumentParser(description = f"""BibleMate AI Web API Client Options""")
parser.add_argument("default", nargs="*", default=None, help="user query")
parser.add_argument("-l", "--language", action="store", dest="language", help="language option; `eng` by defatul; set this option to `tc` or `sc` to override")
parser.add_argument("-t", "--token", action="store", dest="token", help=f"custom token to get acccess to custom data")
parser.add_argument("-u", "--url", action="store", dest="url", help=f"custom token to get acccess to custom data")
args = parser.parse_args()

def main():
    # 1. Define the URL (ensure your BibleMate Web is running)
    url = args.url if args.url else os.getenv("BM_API_ENDPOINT", "http://localhost:33355/api/data")
    # 2. Define your parameters
    payload = {
        "query": " ".join(args.default) if args.default else ".help", # Required
        "language": args.language if args.language else "eng", # Optional
        "token": args.token if args.token else os.getenv("BM_API_CUSTOM_KEY", "") # Optional
    }
    # 3. Send the GET request
    try:
        response = requests.get(url, params=payload)
        
        # 4. Check if the request was successful (Status Code 200)
        if response.status_code == 200:
            data = response.json()  # Convert JSON response to Python dict
            #print("Success!")
            #print(f"Response: {data}")
            api_content = data.get("content", "[NO_CONTENT]")
            if api_content == "\n\n":
                api_content = "[NO_CONTENT]"
            Console().print(Markdown(api_content))
        else:
            print(f"Error: {response.status_code}")
            #print(response.text)
    except requests.exceptions.ConnectionError:
        print("Could not connect to BibleMate API Server. Is it running?")

if __name__ == "__main__":
    main()