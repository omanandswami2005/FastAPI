from fastapi import FastAPI, HTTPException
from requests_html import HTMLSession
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Pydantic model for the profile
class LeetCodeProfile(BaseModel):
    username: str
    real_name: str = None
    ranking: int = None
    problems_solved: int = None
    acceptance_rate: float = None


app = FastAPI()

# Enable CORS to allow access from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fetching profile data from LeetCode
def fetch_leetcode_profile(username: str) -> LeetCodeProfile:
    session = HTMLSession()
    url = f"https://leetcode.com/{username}/"

    try:
        response = session.get(url, timeout=10)  # Adding timeout
    except Exception as e:
        raise HTTPException(status_code=504, detail="Timeout fetching profile")

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Parsing the user's profile data (adjust the selectors as needed)
        real_name = response.html.find(".realname", first=True).text
        ranking = int(response.html.find(".ranking", first=True).text.replace(",", ""))
        problems_solved = int(response.html.find(".total-solved h4", first=True).text)
        acceptance_rate = float(response.html.find(".text-green", first=True).text.strip('%'))

        return LeetCodeProfile(
            username=username,
            real_name=real_name,
            ranking=ranking,
            problems_solved=problems_solved,
            acceptance_rate=acceptance_rate,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error parsing profile")


# Root route for Hello World
@app.get("/")
async def root():
    return {"message": "Hello World"}


# Route to get LeetCode profile
@app.get("/profile/{username}", response_model=LeetCodeProfile)
async def get_profile(username: str):
    try:
        profile = fetch_leetcode_profile(username)
        return profile
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error")


# The app entry point for production
if __name__ == "__main__":
    # This block ensures that Uvicorn handles the app during deployment
    uvicorn.run("leetcode:app", host="0.0.0.0", port=8000, reload=True)