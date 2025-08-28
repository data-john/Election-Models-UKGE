# UK Election Simulator 🗳️

A web-based application for modeling and predicting UK General Election outcomes with customizable polling data and demographic parameters.

## Quick Start

### Prerequisites
- Python 3.11+
- pip or conda

### Installation & Running

1. **Clone the repository**
   ```bash
   git clone https://github.com/data-john/Election-Models-UKGE.git
   cd Election-Models-UKGE
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run src/app.py
   ```

5. **Open your browser** to `http://localhost:8501`

## Project Status - Sprint 1 Complete ✅

### Current Features (Sprint 1)
- ✅ Basic Streamlit application structure
- ✅ Sample polling data display
- ✅ Interactive poll table with filtering
- ✅ Simple polling trend visualization  
- ✅ Basic responsive UI with custom styling
- ✅ Docker containerization ready
- ✅ Unit testing framework

### Coming Next (Sprint 2)
- 🔄 Real polling data integration from Wikipedia
- 🔄 Data caching and refresh functionality
- 🔄 Advanced poll filtering and pollster selection

## Technology Stack

- **Frontend/Backend**: Streamlit (Python full-stack)
- **Data Processing**: pandas, NumPy
- **Visualization**: Streamlit charts, Altair
- **Testing**: pytest
- **Deployment**: Docker, Streamlit Cloud

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Running with Docker
```bash
docker build -t uk-election-simulator .
docker run -p 8501:8501 uk-election-simulator
```

## Project Structure
```
├── src/
│   └── app.py              # Main Streamlit application
├── tests/
│   ├── conftest.py         # Test configuration
│   └── test_basic_app.py   # Basic app tests
├── docs/                   # Project documentation
├── data/                   # Data files (future use)
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
└── README.md              # This file
```

## Contributing

This project follows an 8-week Agile development cycle with weekly sprints. See `docs/agile_implementation_plan.md` for detailed sprint planning.

## License

MIT License - see LICENSE file for details.

## Live Demo

🌐 **Coming Soon**: www.electionmodels.com/UKGE (Sprint 1 deployment target)
