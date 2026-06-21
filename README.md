# 🌿 Carbly

> Know your impact. Change your story.

Carbly is a full-stack Carbon Footprint Awareness Platform designed to help users understand, track, and reduce their personal carbon footprint through a warm AI-powered conversational interface and a dynamic glassmorphism dashboard.

## Chosen Vertical
Carbon Footprint Awareness Platform.

## Approach & Logic
Carbly uses a three-step flow to maximize user engagement and accuracy:
1. **Conversational Onboarding**: Instead of a boring form, users chat with a Google Gemini-powered AI assistant that asks 13 lifestyle questions one by one.
2. **Carbon Calculator**: The collected data is parsed into a specific JSON structure (`carbly_data`), and processed using India-specific emission factors to calculate the footprint in kg CO₂.
3. **Personalised Actions**: Based on the specific data points (e.g., AC usage, car type, diet), the Action Engine ranks and suggests the top 5 most impactful ways to reduce emissions.

## How it Works
```text
[User] <--> [Tailwind/JS Frontend] <--> [FastAPI Backend]
                    |                          |
               (carbly_data)             (gemini_service.py)
                    |                          |
                    v                          v
              [Dashboard UI]          [Google Gemini API]
              - Score & Charts
              - Top Actions
              - Equivalences
                    ^
                    |
              (calculate)
                    |
             [calculator.py]
```
**User Flow:** Landing Page -> AI Chat Onboarding (13 questions) -> Dashboard unlocks with score, benchmarks, and actionable insights.

## Unique Features
- **Hybrid Onboarding**: Users can choose between a conversational AI chat onboarding or a lightning-fast 5-step Quick Form.
- **"Carbon Karma" Gamification**: A complete XP system! Users level up from "Seedling" to "Earth Champion" by logging data, hitting footprint goals, and completing sustainability tasks.
- **Achievements & Badges**: 12 custom India-themed unlockable badges (e.g., "Metro Mover", "Ganga Guardian") with celebratory confetti animations.
- **"Your Earth" Widget**: A dynamic, animated SVG planet on the dashboard that shifts from lush green to smoggy amber depending on the user's carbon score.
- **Weekly Progress & Goals**: LocalStorage-powered data persistence to track a 7-day footprint line chart, 30-day login streak heatmap, and a personal goals memory bank.
- **AI Coach with Markdown**: A slide-out persistent AI assistant that renders rich markdown tables, bold text, and lists for beautiful, scannable data formatting.
- **Glassmorphism Design**: Sleek animated aurora background with frosted glass cards.

## India-Specific Adaptations
- **Grid Factor**: Uses `0.82 kg CO₂/kWh` based on CEA 2023 data.
- **Cooking Fuel**: Calculates based on standard 14.2 kg LPG cylinders.
- **Transport**: Includes metrics for autos, metros, and distinguishes between EV and petrol 2-wheelers.
- **Diet**: Includes specific calculations for common Indian dietary patterns (e.g., veg vs non-veg frequencies).

## Setup & Run Locally
1. Clone the repository: `git clone <YOUR_GITHUB_REPO_URL>`
2. Navigate to the directory: `cd carbly`
3. Install dependencies: `pip install -r requirements.txt`
4. Set your environment variable:
   - Create a `.env` file (see `.env.example`).
   - Add `GEMINI_API_KEY=your_gemini_api_key`
5. Run the server: `uvicorn main:app --reload`
6. Open your browser and go to `http://127.0.0.1:8000`

## Deploy to Cloud Run
To containerise and deploy to Google Cloud Run (asia-south1):

```bash
# Build and push
docker build -t gcr.io/YOUR_PROJECT/carbly .
docker push gcr.io/YOUR_PROJECT/carbly

# Deploy
gcloud run deploy carbly \
  --image gcr.io/YOUR_PROJECT/carbly \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_gemini_api_key \
  --port 8080
```

## Assumptions Made
- Emission factors are averages tailored to India (e.g., 0.82 for electricity, 0.192 for petrol car km).
- Average domestic flight distance is assumed to be 800km.
- Fast fashion clothing item is estimated at 10.0 kg CO₂ per garment.
- Daily steps track avoided car trips indirectly in future updates (currently a lifestyle metric).

## Tech Stack
- **Frontend**: HTML5, Vanilla JS, Tailwind CSS (via CDN), Chart.js (via CDN), Marked.js (via CDN), Canvas-Confetti (via CDN).
- **Backend**: Python 3.11, FastAPI, Uvicorn.
- **AI Integration**: Google Gemini API (`gemini-2.5-flash`).
- **Data Persistence**: Browser `localStorage` (No database required, making the app blazingly fast and fully private).
- **Testing**: Pytest.
- **Deployment**: Docker, Google Cloud Run.
