# Vibe Matcher - Fashion Recommendation System

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB
- OpenAI API key or Emergent LLM key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="fashion_vibes_db"
CORS_ORIGINS="*"
EMERGENT_LLM_KEY="your-key-here"  # Or use OPENAI_API_KEY
```

5. Start backend server:
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
yarn install
```

3. Create `.env` file:
```bash
REACT_APP_BACKEND_URL=http://localhost:8001
```

4. Start development server:
```bash
yarn start
```

### Usage

1. Open browser at `http://localhost:3000`
2. The app will automatically seed 10 fashion products on first load
3. Enter a vibe query like "cozy comfortable loungewear"
4. Click "Find Matches" to see top 3 similar products
5. View metrics and full catalog in other tabs

### API Endpoints

- `GET /api/products` - Get all products
- `POST /api/products` - Create new product
- `POST /api/products/seed` - Seed sample products
- `POST /api/search` - Search by vibe query
- `GET /api/metrics` - Get search metrics

### Key Features

- **Semantic Search**: Uses OpenAI embeddings for understanding vibes
- **Cosine Similarity**: Matches products based on vector similarity
- **Real-time Metrics**: Track latency, scores, and search history
- **Beautiful UI**: Modern design with gradients and animations
- **Edge Cases**: Handles no-match scenarios gracefully

### Tech Stack

- **Backend**: FastAPI + emergentintegrations
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Database**: MongoDB
- **AI**: OpenAI text-embedding-3-small
- **Vector Math**: scikit-learn cosine similarity

### Notes

- Adjust similarity threshold (default 0.7) in search query
- Limit results (default 3, max 10) via API
- Metrics stored in MongoDB for analysis
- Images from Unsplash for demo purposes

