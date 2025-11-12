# Here are your Instructions
Vibe Matcher — AI-Powered Fashion Recommendation System

Vibe Matcher is an intelligent fashion recommendation system that matches clothing items based on vibes — such as boho, urban, cozy, or minimalist.
It uses AI embeddings (OpenAI / Emergent LLM) to understand the text “vibe” and recommend the most similar products from a MongoDB database.

🚀 Features

🧠 AI-Powered Embeddings – Uses OpenAI or Emergent LLM API to generate text embeddings for vibe matching.

👗 Smart Product Matching – Find clothing items that match the user’s vibe query using cosine similarity.

⚙️ FastAPI Backend – Built with Python FastAPI and MongoDB for scalable performance.

💅 React Frontend – A beautiful, interactive interface built with React and Tailwind.

📊 Analytics Dashboard – View search metrics and query performance.

🌐 CORS-Enabled API – Secure backend communication with frontend.

🧩 Tech Stack
Layer	Technology
Backend	FastAPI, Python, Motor (MongoDB driver), NumPy
Frontend	React.js, Vite or CRA (with CRACO), Tailwind CSS
Database	MongoDB
AI / NLP	OpenAI API (text-embedding-3-small) or Emergent LLM
Dev Tools	dotenv, Uvicorn, npm, Node.js
⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/your-username/vibe-matcher.git
cd vibe-matcher

2️⃣ Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate  # (Windows)
pip install -r requirements.txt

Create a .env file in the backend folder:
MONGO_URL=mongodb://localhost:27017
DB_NAME=fashion_vibes_db
CORS_ORIGINS=*
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
# or use EMERGENT_LLM_KEY instead
EMERGENT_LLM_KEY=sk-emergent-xxxxxxxxxxxx

Start MongoDB

Make sure MongoDB is running locally:

"C:\Program Files\MongoDB\Server\8.2\bin\mongod.exe"

Run the Backend
uvicorn server:app --reload --port 8001


Backend runs on http://localhost:8001

3️⃣ Frontend Setup
cd ../frontend
npm install --legacy-peer-deps


If you see missing config errors:

Create a public/index.html

Create craco.config.js if needed for customization.

Start the Frontend
npm start


Frontend runs on http://localhost:3000

🧠 API Endpoints
Endpoint	Method	Description
/api/	GET	Root test endpoint
/api/products	GET	Fetch all products
/api/products	POST	Add new product (auto-generates embedding)
/api/products/seed	POST	Seed sample fashion data
/api/search	POST	Find matching products based on vibe
/api/metrics	GET	View query metrics
/api/products/all	DELETE	Delete all products
🪄 Example: Search Query

POST → /api/search

{
  "vibe": "romantic elegant feminine",
  "limit": 3,
  "threshold": 0.7
}


Response:

{
  "results": [
    {
      "name": "Romantic Silk Blouse",
      "similarity_score": 0.89
    }
  ],
  "metrics": {
    "latency_ms": 152.4,
    "results_count": 1
  }
}

🌱 Seeding Demo Data

You can auto-add 10 fashion items for testing:

POST /api/products/seed


Then use /api/search to try vibe queries like "boho", "urban", or "cozy".

📊 Future Enhancements

🧬 Multimodal Embeddings (Image + Text)

🛍️ E-commerce Integration (Add to cart / buy)

🔍 Better filtering & product categories

🎨 UI theme customization
