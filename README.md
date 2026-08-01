# Rubik Sol AI

An AI-powered Rubik's Cube solver that uses Google Gemini Vision to detect cube colors from photos and computes optimal solutions using Kociemba's two-phase algorithm.

## Features

- **AI-Powered Color Detection**: Upload photos of your cube's faces and let Google Gemini Vision identify the sticker colors automatically
- **Manual Color Input**: Click on cells to cycle through colors as an alternative to photo upload
- **Optimal Solutions**: Uses Herbert Kociemba's two-phase algorithm to find efficient solutions (typically 20 moves or fewer)
- **Interactive Solution Display**: Step through the solution move-by-move with visual guidance
- **Solve History**: Automatically saves and tracks all your solves
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Technologies

### Backend
- **Django 5.1.1** - Web framework
- **Google Generative AI** - Gemini Vision API for color detection
- **Gunicorn** - Production WSGI server
- **WhiteNoise** - Static file serving

### Frontend
- **Bootstrap 5.3.3** - Responsive UI framework
- **jQuery 3.7.1** - DOM manipulation
- **Custom JavaScript** - Cube solver implementation (Kociemba algorithm)

## Installation

### Prerequisites
- Python 3.x
- Google Gemini API key

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aayan216/RUBIK-SOL-v1.git
   cd RUBIK-SOL-v1
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Open your browser**
   
   Navigate to `http://127.0.0.1:8000/`

## Usage

1. **Capture Cube Faces**: Take photos of each face of your Rubik's Cube, or manually select colors by clicking on the grid cells
2. **Detect Colors**: Click "Detect Colors" to have AI identify the sticker colors from your photos
3. **Solve**: Once all 6 faces are entered, click "Solve Cube" to get the solution
4. **Follow the Solution**: Use the Previous/Next buttons to step through each move with visual guidance
5. **View History**: Check your past solves in the History section

## Project Structure

```
RUBIK-SOL-v1/
├── rubiks_project/          # Django project configuration
│   ├── settings.py          # Project settings
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI entry point
├── solver/                  # Main application
│   ├── views.py             # View functions
│   ├── vision.py            # Gemini Vision integration
│   ├── validators.py        # Cube state validation
│   ├── models.py            # Database models
│   └── templates/           # HTML templates
├── static/                  # Static assets
│   ├── css/                 # Stylesheets
│   └── js/                  # JavaScript (cube solver)
├── requirements.txt         # Python dependencies
├── Procfile                 # Heroku deployment config
└── manage.py                # Django management script
```

## How It Works

1. **Color Detection**: Photos are sent to Google Gemini Vision with prompts asking it to identify the 3x3 grid of sticker colors (white, yellow, red, orange, blue, green)

2. **Validation**: The app validates the cube state ensuring:
   - All 6 faces are present with 9 stickers each
   - Each color appears exactly 9 times
   - Center stickers are all different colors
   - The configuration is physically solvable

3. **Solving**: The solver runs entirely in the browser using Kociemba's two-phase algorithm:
   - **Phase 1**: Reduces the cube to a specific subgroup
   - **Phase 2**: Solves the cube within that subgroup

4. **Display**: The solution is presented as a sequence of moves with step-by-step navigation

## Deployment

The project is configured for deployment on platforms like Heroku:

```bash
# Collect static files
python manage.py collectstatic

# The Procfile is already configured:
# web: gunicorn rubiks_project.wsgi:application
```

For production, ensure you set:
- `DEBUG = False` in settings.py
- `DJANGO_SECRET_KEY` environment variable
- `ALLOWED_HOSTS` environment variable
- `GEMINI_API_KEY` environment variable

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Your Google Gemini API key for vision capabilities |
| `DJANGO_SECRET_KEY` | Django secret key (for production) |
| `DEBUG` | Set to `False` in production |

## License

This project is open source and available under the MIT License.

## Acknowledgments

- **Herbert Kociemba** - For the two-phase algorithm implementation
- **Google Gemini** - For powerful vision capabilities
- **Django Community** - For the excellent web framework
