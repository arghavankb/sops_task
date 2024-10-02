import os
import aiohttp
from serpapi import GoogleSearch
from PIL import Image
from io import BytesIO
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from .models import Image as ImageModel
from .db import async_session
from dotenv import load_dotenv


load_dotenv()

SERP_API_KEY = os.getenv("SERP_API_KEY")


# This function fetches image urls according to search term that you enter in request body by using SerpApi
async def fetch_image_urls(search_term: str, num_images: int):
    # source: https://serpapi.com/search
    search = GoogleSearch({
        "q": search_term,
        "tbm": "isch",
        "api_key": SERP_API_KEY
    })

    try:
        results = search.get_dict()
        image_urls = [result["original"] for result in results["images_results"][:num_images]]

        return image_urls

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch image URLs: {str(e)}")



# This function downloads image urls that you fetched
async def download_image(session, url: str) -> BytesIO:
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return BytesIO(await response.read())
            else:
                raise HTTPException(status_code=response.status, detail=f"Failed to download image: {response.status}")

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while downloading the image: {str(e)}")



# This function resizes the downloaded images according to the size and format you specify
async def resize_image(image_data: BytesIO, size=(10, 10)) -> BytesIO:
    try:
        image = Image.open(image_data)
        image = image.resize(size)
        resized_image = BytesIO()
        image.save(resized_image, format=os.getenv("IMAGE_FORMAT"))
        resized_image.seek(0)

        return resized_image

    except(IOError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Failed to resize image: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resize image: {str(e)}")



# This function stores data in Image table of the database
async def store_image(session: AsyncSession, image_url, image_data: BytesIO, search_term):
    try:
        new_image = ImageModel(
            url = image_url,
            image_data=image_data.read(),
            search_term=search_term
        )
        session.add(new_image)
        await session.commit()

    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to store image: {str(e)}")



async def process_images(search_term: str, num_images: int):
    try:
        image_urls = await fetch_image_urls(search_term, num_images)

        async with aiohttp.ClientSession() as http_session:
            async with async_session() as session:
                for url in image_urls:
                    try:
                        image_data = await download_image(http_session, url)
                        if image_data:
                            resized_image = await resize_image(image_data)
                            await store_image(session, url, resized_image, search_term)

                    except HTTPException as e:
                        raise HTTPException(status_code=400, detail=f"Error processing image {url}: {e.detail}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
