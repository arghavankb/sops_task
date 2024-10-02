import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.image_processor import fetch_image_urls, download_image, resize_image, store_image, process_images
from fastapi import HTTPException
from io import BytesIO
from PIL import Image
from aiohttp import ClientSession, ClientResponseError
from app.models import Image
from sqlalchemy.exc import SQLAlchemyError



# Unit test for "fetch_image_urls" function:
@pytest.mark.asyncio
async def test_fetch_image_urls_success():
    mock_results = {
        "images_results": [
            {"original": "https://example.com/image1.jpg"},
            {"original": "https://example.com/image2.jpg"}
        ]
    }

    with patch("app.image_processor.GoogleSearch") as mock_search:
        mock_instance = MagicMock()
        mock_instance.get_dict.return_value = mock_results
        mock_search.return_value = mock_instance

        image_urls = await fetch_image_urls("test search", 2)

        assert image_urls == ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]


@pytest.mark.asyncio
async def test_fetch_image_urls_exception_handling():
    with patch("app.image_processor.GoogleSearch") as mock_search:
        mock_instance = MagicMock()
        mock_instance.get_dict.side_effect = Exception("API error")
        mock_search.return_value = mock_instance  # Ensure the mock instance is returned

        with pytest.raises(HTTPException) as exc_info:
            await fetch_image_urls("test search", 2)

        assert exc_info.value.status_code == 500
        assert "Failed to fetch image URLs: API error" in str(exc_info.value.detail)




# Unit test for "download_image" function
@pytest.mark.asyncio
async def test_download_image_success():
    url = "http://example.com/image.jpg"
    mock_image_data = b"fake image data"

    mock_session = AsyncMock(spec=ClientSession)
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.read.return_value = mock_image_data
    mock_session.get.return_value.__aenter__.return_value = mock_response

    result = await download_image(mock_session, url)

    assert isinstance(result, BytesIO)
    assert result.getvalue() == mock_image_data


@pytest.mark.asyncio
async def test_download_image_not_found():
    url = "http://example.com/image.jpg"

    mock_session = AsyncMock(spec=ClientSession)
    mock_response = AsyncMock()
    mock_response.status = 404
    mock_session.get.return_value.__aenter__.return_value = mock_response

    with pytest.raises(HTTPException) as exc_info:
        await download_image(mock_session, url)

    assert exc_info.value.status_code == 404
    assert "Failed to download image: 404" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_download_image_exception():
    url = "http://example.com/image.jpg"

    mock_session = AsyncMock(spec=ClientSession)

    mock_request_info = AsyncMock()
    mock_request_info.real_url = url

    mock_response_error = ClientResponseError(
        request_info=mock_request_info,
        history=()
    )

    mock_session.get.side_effect = mock_response_error

    with pytest.raises(HTTPException) as exc_info:
        await download_image(mock_session, url)

    assert exc_info.value.status_code == 500



# Unit test for "resize_image" function
@pytest.fixture
def mock_image_data():
    img = Image.new('RGB', (20, 20), color='red')
    image_data = BytesIO()
    img.save(image_data, format='PNG')
    image_data.seek(0)
    return image_data


@pytest.mark.asyncio
async def test_resize_image_success(mock_image_data):
    size = (10, 10)
    result = await resize_image(mock_image_data, size)

    assert isinstance(result, BytesIO)

    resized_image = Image.open(result)
    assert resized_image.size == size


@pytest.mark.asyncio
async def test_resize_image_invalid_format():
    invalid_image_data = BytesIO(b"not an image")

    with pytest.raises(HTTPException) as exc_info:
        await resize_image(invalid_image_data)

    assert exc_info.value.status_code == 400
    assert "Failed to resize image" in exc_info.value.detail


@pytest.mark.asyncio
async def test_resize_image_unexpected_error(mock_image_data):
    with patch('os.getenv', return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            await resize_image(mock_image_data)

        assert exc_info.value.status_code == 400
        assert "Failed to resize image" in exc_info.value.detail



# Unit test for "store_image" function:
@pytest.mark.asyncio
async def test_store_image_success():
    mock_session = AsyncMock()
    image_url = "http://example.com/image.jpg"
    mock_image_data = BytesIO(b"fake image data")
    search_term = "example"

    await store_image(mock_session, image_url, mock_image_data, search_term)

    mock_session.add.assert_called_once()
    new_image = mock_session.add.call_args[0][0]
    assert isinstance(new_image, Image)
    assert new_image.url == image_url
    assert new_image.image_data == mock_image_data.getvalue()
    assert new_image.search_term == search_term

    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_store_image_database_error():
    mock_session = AsyncMock()
    image_url = "http://example.com/image.jpg"
    mock_image_data = BytesIO(b"fake image data")
    search_term = "example"

    mock_session.commit.side_effect = SQLAlchemyError("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await store_image(mock_session, image_url, mock_image_data, search_term)

    assert exc_info.value.status_code == 500
    assert "Database error" in str(exc_info.value.detail)
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_store_image_general_error():
    mock_session = AsyncMock()
    image_url = "http://example.com/image.jpg"
    mock_image_data = BytesIO(b"fake image data")
    search_term = "example"

    mock_session.commit.side_effect = Exception("General error")

    with pytest.raises(HTTPException) as exc_info:
        await store_image(mock_session, image_url, mock_image_data, search_term)

    assert exc_info.value.status_code == 500
    assert "Failed to store image: General error" in str(exc_info.value.detail)
    mock_session.rollback.assert_awaited_once()



# Unit test for "process_images" function
@pytest.mark.asyncio
async def test_process_images_success():
    search_term = "test"
    num_images = 2

    with patch('app.image_processor.fetch_image_urls', new_callable=AsyncMock) as mock_fetch, \
            patch('app.image_processor.download_image', new_callable=AsyncMock) as mock_download, \
            patch('app.image_processor.resize_image', new_callable=AsyncMock) as mock_resize, \
            patch('app.image_processor.store_image', new_callable=AsyncMock) as mock_store:
        mock_fetch.return_value = ['http://example.com/image1.jpg', 'http://example.com/image2.jpg']

        mock_download.return_value = AsyncMock()

        await process_images(search_term, num_images)

        mock_fetch.assert_called_once_with(search_term, num_images)
        assert mock_download.call_count == 2
        assert mock_resize.call_count == 2
        assert mock_store.call_count == 2
