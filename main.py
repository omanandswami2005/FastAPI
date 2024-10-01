from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import uvicorn

app = FastAPI()

# Enable CORS to allow access from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace the Pydantic model and create a function to fetch the LeetCode profile using GraphQL API
def fetch_leetcode_profile(username: str):
    url = "https://leetcode.com/graphql/"
    headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "",
    "Content-Type": "application/json",
    "baggage": "sentry-environment=production,sentry-release=7366c15b,sentry-transaction=%2Fu%2F%5Busername%5D,sentry-public_key=2a051f9838e2450fbdd5a77eb62cc83c,sentry-trace_id=cd58a4991f3d4ad082c1adf54451481a,sentry-sample_rate=0.03",
}

    query = {
        "query": """
        query userPublicProfile($username: String!) {
            matchedUser(username: $username) {
                username
                githubUrl
                twitterUrl
                linkedinUrl
                profile {
                    ranking
                    userAvatar
                    realName
                    aboutMe
                    school
                    countryName
                    reputation
                    company
                    solutionCount
                    postViewCount
                }
                contestBadge {
                    name
                    expired
                    hoverText
                    icon
                    
                }
            }
        }
        """,
        "variables": {
            "username": username
        },
        "operationName": "userPublicProfile"
    }

    response = requests.post(url, headers=headers, json=query)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching profile")

    try:
        data = response.json().get("data", {}).get("matchedUser", None)
        if data:
            return {"status": "ok", "profile": data}
        else:
            raise HTTPException(status_code=404, detail="Profile not found")
    except requests.exceptions.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding response")

# Root route for Hello World
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Route to get LeetCode profile
@app.get("/profile/{username}")
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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
