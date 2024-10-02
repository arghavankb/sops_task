from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

def test_search_image():
    response = client.post(
        "/search-images/",
        json={
            "search_term" : "puppy",
            "num_images": 3
        })

    assert response.status_code == 200
    assert response.json() == {"message": "Images are downloaded and stored successfully."}