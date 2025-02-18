# HealthyRemote

## Overview
HealthyRemote is a wellness platform designed for remote workers. It helps users track their activities, stress levels, weight, and other health metrics to maintain a healthy lifestyle while working remotely.

## Features
- User authentication (login and sign up)
- Track daily activities
- Log stress levels
- Record weight measurements
- Conduct mobility tests
- Participate in wellness challenges
- View comprehensive user data on the dashboard

## Technologies Used
- Python
- Streamlit
- PostgreSQL (hosted on Neon)
- psycopg2
- dotenv

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database (Neon)

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/HealthyRemote.git
   cd HealthyRemote
   ```

2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your database URL:
   ```properties
   DATABASE_URL=''
   ```

5. Initialize the database:
   ```sh
   python -c "from utils.database import init_db; init_db()"
   ```

### Running the Application
1. Run the Streamlit application:
   ```sh
   streamlit run Home.py
   ```

2. Open your web browser and go to `http://localhost:8501` to access the application.

## Deployment
To deploy the application to Streamlit, follow these steps:
1. Push your code to GitHub.
2. Go to the Streamlit deployment dashboard.
3. Select your repository and branch.
4. Set the `DATABASE_URL` environment variable in the Streamlit deployment settings.

## Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes.