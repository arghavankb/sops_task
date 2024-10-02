from fastapi import APIRouter
from .image_processor import process_images
from .schemas import SearchRequestSchema

router = APIRouter()


@router.post("/search-images/")
async def search_images(request: SearchRequestSchema):
    await process_images(request.search_term, request.num_images)
    return {"message": "Images are downloaded and stored successfully."}
