# Chemical Equipment Visualizer

Hybrid Web Application and Desktop Application for analyzing equipment parameters.

## Setup

### Backend
Open terminal in `backend` folder.

1.  **Initialize environment:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    pip install django djangorestframework django-cors-headers pandas matplotlib
    ```

2.  **Run migrations and server:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```
    The API will be available at http://127.0.0.1:8000/.

### Frontend
Open new terminal in the project root folder.

1.  **Install dependencies:**
    ```bash
    npm install
    ```

2.  **Start dev server:**
    ```bash
    npm run dev
    ```
    The web dashboard uses React and Vite.

### Desktop App
**Setup & Run**
Ensure the Django backend is running in another terminal.

1.  **Run the desktop app using the helper script:**
    ```cmd
    ./run_desktop_app.bat
    ```

2.  **Or manually:**
    ```bash
    pip install -r desktop_app/requirements.txt
    python desktop_app/main.py
    ```

## Features

-   **Upload:** Support for CSV dataset uploads.
-   **Analytics:** Automated calculation of parameter averages for Flowrate, Pressure, and Temperature.
-   **Visuals:** Equipment Type Distribution (Pie Chart) and Parameter Averages (Bar Chart).
-   **History:** Tracks and displays the last 5 dataset uploads with unique IDs and timestamps.
-   **Report:** Capability to download summarized reports of the processed data.
