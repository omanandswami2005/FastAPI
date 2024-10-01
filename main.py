from fastapi import FastAPI
from requests_html import HTMLSession
from pydantic import BaseModel

app = FastAPI()

# Pydantic model for the profile
class LeetCodeProfile(BaseModel):
    username: str
    real_name: str = None
    ranking: str = None
    problems_solved: str = None
    acceptance_rate: str = None


def fetch_leetcode_profile(username: str) -> LeetCodeProfile:
    session = HTMLSession()
    url = f"https://leetcode.com/{username}/"
    response = session.get(url)

    if response.status_code != 200:
        raise ValueError("User not found")

    # Parsing the user's profile data (adjust the selectors as needed)
    real_name = response.html.find(".realname", first=True).text
    ranking = response.html.find(".ranking", first=True).text
    problems_solved = response.html.find(".total-solved h4", first=True).text
    acceptance_rate = response.html.find(".text-green", first=True).text

    return LeetCodeProfile(
        username=username,
        real_name=real_name,
        ranking=ranking,
        problems_solved=problems_solved,
        acceptance_rate=acceptance_rate,
    )


@app.get("/profile/{username}", response_model=LeetCodeProfile)
async def get_profile(username: str):
    try:
        profile = fetch_leetcode_profile(username)
        return profile
    except ValueError as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
