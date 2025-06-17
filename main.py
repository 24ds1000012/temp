from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Enable CORS for all origins (development use)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"]
)

WIKI_BASE_URL = "https://en.wikipedia.org/wiki/"

class OutlineResponse(BaseModel):
    outline: str

@app.get("/api/outline", response_model=OutlineResponse)
async def get_outline(query: str) -> OutlineResponse:
    complete_url = WIKI_BASE_URL + query
    response = requests.get(complete_url, verify=False)

    if response.status_code != 200:
        return OutlineResponse(outline=f"Failed to fetch article for '{query}'. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")
    headings = []

    for level in range(1, 7):
        for tag in soup.find_all(f'h{level}'):
            text = tag.get_text(strip=True)
            if text:
                prefix = "#" * level
                headings.append(f"{prefix} {text}")

    if not headings:
        return OutlineResponse(outline=f"No headings found for '{query}'.")

    # Build formatted Markdown outline
    outline_lines = []
    for heading in headings:
        level = heading.count('#')
        text = heading.lstrip('#').strip()
        if level == 1 and outline_lines:
            outline_lines.append("")  # Add spacing between main sections
        outline_lines.append(f"{'#' * level} {text}")

    outline = "Contents\n\n" + "\n".join(outline_lines)
    return OutlineResponse(outline=outline.strip())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
