from pydantic import BaseModel

class SearchRequestSchema(BaseModel):
    search_term: str
    num_images: int
