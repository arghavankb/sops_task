# Google Image Downloader

## Description
Google Image Downloader is a Python-based project that allows users to easily search for a specific term on Google Images and download a customizable number of images by calling an API. 

## Table of Contents
- [Sign Up and Get a SerpApi API Key](#sign-up-and-get-a-serpapi-api-key)
- [Installation Instructions](#installation-instructions)
- [Usage](#usage)
- [Technologies Used](#technologies-used)
- [Contact Information](#contact-information)

## Sign Up and Get a SerpApi API Key
  - Visit the [SerpApi website](https://serpapi.com).
  - Create an account and log in.
  - After logging in, you will receive an API key that you will use to authenticate your requests.

## Installation Instructions
1. **Clone the repository**
   ```bash
   git clone https://github.com/arghavankb/sops_task.git
2. **Navigate to the project directory**
   ```bash
   cd sops_task
3. **Create a virtual environment for the Python project**
   ```bash
   python -m venv venv
4. **Activate the virtual environment on Ubuntu**
   ```bash
   source venv/bin/activate
5. **Run Docker using the following command**
   
   Don't forget to choose appropriate `DATABASE_URL` and `host`
   ```bash
   docker compose up --build

## Usage
After running Docker on your local machine, you can access the FastAPI Swagger at [http://localhost:8000/docs](http://localhost:8000/docs).

In the Swagger interface, you can enter the `search_term` and `num_images` in the request body. The image binary data and the URLs of the images will then be stored in the `image` table of the PostgreSQL database running within the Docker container.

## Technologies Used
- **Python**: Core language for implementing the project.
- **FastAPI**: Framework used for building the API.
- **Docker**: Containerization platform used to deploy the application.
- **PostgreSQL**: Database used to store image data.
- **SerpApi**: API used for fetching Google image search results.

## Contact Information
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:arghavan.kb@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/arghavankb)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/arghavan-kb-680216/)
