Installation:
pip install -r requirements.txt
playwright install


Running the app:
uvicorn app:app --reload

==============================
Build the Docker image (Converts your code + dependencies into a runnable image)
From the project root run
docker build -t myapp .

Run the container
docker run -p 8000:8000 myapp

When the container is running you can access the front-end on 
http://localhost:8000


==============================
Deploy to VPS
git clone your-repo
cd myapp
docker build -t myapp .
docker run -d -p 80:8000 myapp