# HealthyRemote: Wellness Platform for Remote Workers

## Overview
HealthyRemote is a comprehensive wellness platform designed for remote workers. It helps users track their health metrics, participate in challenges, access educational content, and receive AI-powered wellness assistance to maintain a healthy lifestyle while working remotely.

## Live Demo
**Try the live application**: [https://healthyremote.streamlit.app/](https://healthyremote.streamlit.app/)

**Test credentials**:
- Username: paco | Email: paco@example.com
- Username: paca | Email: paca@example.com

## Features

### Health Tracking
- Track daily activities with duration and type
- Monitor stress levels over time
- Record weight measurements for BMI calculation
- Conduct mobility self-assessments

### Wellness Support
- AI Wellness Assistant for personalized guidance
- Participate in structured wellness challenges
- Educational content on ergonomics and stretching
- Background music integration via Spotify

### Data Visualization
- Interactive dashboards showing health trends
- Comprehensive progress reports
- Downloadable PDF wellness reports
- BMI interpretation and recommendations

### User Experience
- Personalized user profiles
- Multi-page interface with intuitive navigation
- Authentication system (login and registration)
- Mobile-responsive design

## Technologies Used
- **Python**: Core programming language
- **Streamlit**: Web application framework
- **PostgreSQL/Neon**: Database for user data storage
- **OpenAI API**: Powers the AI wellness assistant
- **ReportLab**: Generates PDF wellness reports
- **Plotly**: Interactive data visualizations
- **Pandas/NumPy**: Data processing and analysis
- **Spotify Web Embed**: Background music player

## Project Structure
- **Home.py**: Main dashboard and entry point
- **pages/**
  - **1_Assessment.py**: Health assessments and tracking
  - **2_Progress.py**: Health metrics visualization and reports
  - **3_Education.py**: Ergonomics and wellness education
  - **4_Assistant.py**: AI wellness assistant interface
- **utils/**
  - **components.py**: Core functionality including AI assistant, BMI interpreter, and Spotify player
  - **database.py**: Database operations, schema definition, and data access
  - **pdf_generator.py**: PDF wellness report generation
  - **recommendations.py**: Dynamic health recommendations and tips
  - **visualization.py**: Data visualization helpers
  - **wellness_tips.py**: Wellness tips and advice
- **data/**
  - **db_samples/**: Sample database records for testing and demos
  - **images/**: Images for self-assessment tests
- **.env**: Environment variables for configuration
- **requirements.txt**: Python dependencies

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database (Neon)
- OpenAI API key

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

4. Create a .env file in the root directory and add your credentials:
   ```properties
   DATABASE_URL=''
   OPENAI_API_KEY=''
   ```

5. Initialize the database:
   ```sh
   python -c "from utils.database import init_db; init_db()"
   ```

### Running the Application
1. Start the Streamlit application:
   ```sh
   streamlit run Home.py
   ```

2. Open your web browser and go to `http://localhost:8501` to access the application.

## Running with Docker
HealthyRemote is containerized for easy deployment in any environment.

### Prerequisites for Docker
- Docker installed on your machine
- Docker Compose (optional, for easier management)

### Using Docker
1. Build the Docker image:
   ```sh
   docker build -t healthyremote .
   ```

2. Run the container:
   ```sh
   docker run -p 8501:8501 --env-file .env healthyremote
   ```

3. Access the application at `http://localhost:8501`

### Using Docker Compose
1. Start the application using the provided docker-compose.yml:
   ```sh
   docker-compose up
   ```

2. Access the application at `http://localhost:8501`

## Deployment
To deploy the application to Streamlit Cloud:
1. Push your code to GitHub
2. Go to the Streamlit Cloud dashboard
3. Connect your GitHub repository
4. Add the required environment variables (DATABASE_URL, OPENAI_API_KEY)
5. Deploy the application

## Data Directory
The data directory contains important resources that are necessary for the full functionality of the application:

### db_samples/
These files contain sample data for testing and demonstration:
- Sample activities, weights, and stress logs
- Pre-defined challenges and their requirements
- Test user profiles with realistic health data

### images/
Contains all visual assets for the application:
- Mobility test illustrations used in the self-assessment section
- Exercise demonstration images for the education section
- UI elements and icons

To properly run the application, ensure the data directory structure is maintained after cloning the repository.

## Requirements
The application requires several Python packages, which are listed in the `requirements.txt` file. Please install the dependencies using:

```sh
pip install -r requirements.txt
```

## Get Started Today!
Ready to enhance your wellness journey? Access the HealthyRemote application live at [HealthyRemote](https://healthyremote.streamlit.app/). 

Explore the features and see how it can support your health and wellness goals!

If you have any questions, feedback, or contributions, feel free to contact.

Happy remote work, and stay healthy!
