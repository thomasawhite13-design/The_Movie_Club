from typing import List, Optional
from pydantic import BaseModel, Field

### vibe
class Keyword(BaseModel):
    id: int
    name: str

class Keywords(BaseModel):
    keywords: List[Keyword] = []
### vibe

class CrewMember(BaseModel):
    job: str
    name: str

class Credits(BaseModel):
    crew: List[CrewMember] = []

class MovieResult(BaseModel):
    id: int
    title: str
    overview: str
    release_date: str = ""  # Some movies don't have a date
    genre_ids: List[int] = []
    popularity: float
    vote_average: float

class MovieDetail(BaseModel):
    id: int
    title: str
    release_date: str = ""  # ||
    credits: Credits = Field(default_factory=Credits)
    keywords: Keywords = Field(default_factory=Keywords)  # Vibe

class SearchResponse(BaseModel):
    page: int
    results: List[MovieResult]
    total_pages: int
    total_results: int