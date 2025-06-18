# Code Iterator Tool

**Author:** G Gnaneswara Rao

 It functions as a lightweight code assistant, similar to Cursor, designed to help game developers by suggesting and applying code improvements based on user prompts.

## Features (MVP Requirements Met)

*   Accepts selected code input from the user via a textarea.
*   Accepts a natural language prompt describing the desired code change.
*   Connects to a backend API which uses Google Generative AI (Gemini) to generate suggestions.
*   Returns:
    *   A clear explanation of the suggested changes.
    *   The modified code snippet.
*   Provides an "Integrate Code" button to apply the suggested changes directly back into the input textarea.
*   Displays the AI's response (explanation and code) clearly in the UI.
*   Includes basic UI feedback (loading states, error messages).

## Technology Stack

*   **Backend:** Python, FastAPI, Uvicorn
*   **AI Model:** Google Generative AI (Gemini Pro via `google-generativeai` library)
*   **Frontend:** Vanilla JavaScript, HTML5, CSS3 (using TailwindCSS via CDN)
*   **Environment Variables:** `python-dotenv`

## Setup Instructions

### Prerequisites

*   Python 3.8+ installed.
*   `pip` (Python package installer).
*   A Google AI API Key (obtained from [Google AI Studio](https://aistudio.google.com/)).

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd your-project-folder
    ```
2.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
3.  **Create the environment file:**
    *   Create a file named `.env` in the `backend` directory.
    *   Add your Google AI API key to it like this:
        ```dotenv
        GOOGLE_API_KEY=YOUR_GOOGLE_AI_API_KEY_HERE
        ```
    *   **Important:** This `.env` file is listed in `.gitignore` and should **never** be committed to version control.
4.  **Install Python dependencies:**
    ```bash
    # It's recommended to use a virtual environment
    # python -m venv .venv
    # source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

    pip install fastapi uvicorn python-dotenv google-generativeai pydantic "python-multipart" Jinja2 aiofiles
    ```
    *(Note: Add any other specific libraries you might have used)*

### Frontend Setup

*   No specific build steps are required for the frontend. It uses vanilla JavaScript and CSS linked via CDN.

## Running the Application

1.  **Start the backend server:**
    *   Make sure you are in the main `your-project-folder/` directory (or navigate back using `cd ..` if you are still in `backend`).
    *   Run the following command in your terminal:
        ```bash
        uvicorn backend.main:app --reload --port 8000
        ```
    *   The server should start, and you'll see output indicating it's running on `http://127.0.0.1:8000`.
2.  **Access the frontend:**
    *   Open the `frontend/index.html` file directly in your web browser (e.g., by double-clicking it or using `File > Open` in your browser).

## Usage

1.  Paste or type the code snippet you want to modify into the "Your Code" textarea.
2.  Describe the change you want in the "Describe Change" input field (e.g., "Optimize this loop", "Add error handling", "Use f-strings").
3.  Click the "Get Suggestion" button.
4.  Wait for the AI response. The "Explanation" and "Suggested Code" will appear below.
5.  Review the suggestion.
6.  If you like the suggestion, click the "Integrate Code" button to replace the code in the top textarea with the suggested code.

