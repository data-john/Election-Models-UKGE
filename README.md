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

## Project Status - Sprint 1 Day 4 ✅

### Current Features (Sprint 1)
- ✅ Basic Streamlit application structure
- ✅ Sample polling data display
- ✅ Interactive poll table with filtering
- ✅ Simple polling trend visualization  
- ✅ Basic responsive UI with custom styling
- ✅ Docker containerization ready
- ✅ Unit testing framework
- ✅ **Streamlit Cloud deployment configuration**
- 🔄 Domain configuration (ukge.electionmodels.com recommended)

### Coming Next (Sprint 1 Completion)
- 🔄 Production deployment verification (Day 5)
- 🔄 Final smoke testing and optimization (Day 6)

### Future Sprints
- 🔄 Real polling data integration from Wikipedia (Sprint 2)
- 🔄 Data caching and refresh functionality (Sprint 2)
- 🔄 Advanced poll filtering and pollster selection

## Technology Stack

- **Frontend/Backend**: Streamlit (Python full-stack)
- **Data Processing**: pandas, NumPy
- **Visualization**: Streamlit charts, Altair
- **Testing**: pytest
- **Deployment**: Docker, Streamlit Cloud
- **Infrastructure**: Custom domain configuration, SSL certificates

## Deployment

### Live Application
🌐 **Production URL**: www.electionmodels.com/UKGE (configured in Sprint 1 Day 4)

### Deployment Options

#### Option 1: Streamlit Cloud (Production)
1. Configure repository connection
2. Set main file: `src/app.py`
3. Upload secrets via dashboard
4. Configure custom domain
5. See `docs/DEPLOYMENT.md` for detailed instructions

#### Option 2: Local Development
```bash
streamlit run src/app.py
```

#### Option 3: Docker Container
```bash
docker build -t uk-election-simulator .
docker run -p 8501:8501 uk-election-simulator
```

For detailed deployment instructions, see [DEPLOYMENT.md](docs/DEPLOYMENT.md).

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

### Deployment to Streamlit Cloud
See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete deployment instructions including:
- Repository configuration
- Custom domain setup (www.electionmodels.com/UKGE)
- Secrets management
- Production monitoring

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

🌐 **Production Application**: ukge.electionmodels.com (recommended)  
🔄 **Alternative Path**: electionmodels.com/UKGE (redirect setup)  
📊 **Status**: Deployment ready, domain configuration in progress  
🔧 **Infrastructure**: Streamlit Cloud with custom domain  
📖 **Domain Setup Guide**: See [docs/DOMAIN_CONFIGURATION.md](docs/DOMAIN_CONFIGURATION.md)
