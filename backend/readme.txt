Installation:
pip install -r requirements.txt
playwright install


Running the app:
uvicorn app:app --reload

==============================
Build the Docker image called watch-scraper (Converts your code + dependencies into a runnable image)
From the project root run
docker build -t watch-scraper .

Run the container (and also inject the .env file in it)

docker run --name watch-scraper \
  -p 8000:8000 \
  --env-file .env \
  -v "$(pwd):/app" \
  watch-scraper \
  uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload


When the container is running you can access the front-end on 
http://localhost:8000


==============================
Deploy to VPS
git clone your-repo
cd myapp
docker build -t myapp .
docker run -d -p 80:8000 myapp