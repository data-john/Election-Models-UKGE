# UK Election Simulator - Detailed Project Specification

## 1. Project Overview

### 1.1 Purpose
The UK Election Simulator is a web-based application that enables users to model and predict UK General Election outcomes by customizing polling data inputs and demographic clustering parameters. The application provides an interactive interface for exploring how different assumptions about voter behavior and demographic influences affect electoral predictions.

### 1.2 Core Functionality
- Interactive poll selection from multiple pollsters
- Customizable demographic clustering for constituency modeling
- Real-time prediction visualization
- Stratified polling data analysis with demographic swing calculations
- Comprehensive results display showing seat predictions and swing analysis

### 1.3 Target Users
- Political analysts and researchers
- Journalists covering UK politics
- Academic researchers studying electoral behavior
- Political enthusiasts and the general public

## 2. Technical Architecture

### 2.1 System Architecture
```
User Browser
    ↓ HTTP Requests
Streamlit Web Application
    ↓ Data Processing
Python Modeling Engine (pandas, scikit-learn)
    ↓ Data Retrieval
Data Sources (CSV files, GitHub repos, APIs)
```

### 2.2 Technology Stack
- **Backend Framework**: Streamlit (Python-based full-stack solution)
- **Data Processing**: pandas, NumPy
- **Machine Learning**: scikit-learn (KMeans clustering, demographic modeling)
- **Statistical Analysis**: statsmodels
- **Data Visualization**: Streamlit native charts, Altair, matplotlib
- **Data Storage**: SQLite (local caching), CSV files
- **Testing**: pytest
- **Containerization**: Docker
- **Deployment**: Streamlit Cloud (primary), Heroku (backup)

### 2.3 Domain and Hosting
- **Domain**: www.electionmodels.com/UKGE
- **Hosting**: Streamlit Cloud free tier (1GB RAM limit)
- **Backup Hosting**: Heroku free dyno (512MB RAM)

## 3. Functional Requirements

### 3.1 Poll Management
- **FR1.1**: Display all recent UK opinion polls in a sortable table
- **FR1.2**: Allow users to select individual polls or combinations of pollsters
- **FR1.3**: Show poll metadata (date, sample size, methodology, margin of error)
- **FR1.4**: Filter polls by date range, pollster, or sample size
- **FR1.5**: Cache poll data locally to reduce API calls

### 3.2 Demographic Clustering
- **FR2.1**: Allow users to select demographic factors for constituency clustering
- **FR2.2**: Support factors including: age distribution, income levels, education, urbanization, Brexit vote share, previous election results
- **FR2.3**: Use K-means clustering to group constituencies with similar demographics
- **FR2.4**: Display cluster visualization with constituency assignments
- **FR2.5**: Allow users to adjust number of clusters (3-15 range)

### 3.3 Modeling and Prediction
- **FR3.1**: Calculate expected swing per cluster using stratified polling data
- **FR3.2**: Apply demographic weighting to poll data
- **FR3.3**: Generate seat predictions for each political party
- **FR3.4**: Calculate prediction confidence intervals
- **FR3.5**: Show swing analysis compared to previous election results

### 3.4 Results Visualization
- **FR4.1**: Display predicted seat totals in interactive charts
- **FR4.2**: Show constituency-level predictions on an interactive map
- **FR4.3**: Generate swing comparison tables
- **FR4.4**: Export results as CSV or PDF reports
- **FR4.5**: Display model assumptions and methodology explanations

### 3.5 User Interface
- **FR5.1**: Intuitive parameter selection using sliders and dropdowns
- **FR5.2**: Real-time updates as parameters change
- **FR5.3**: Clear loading indicators during model execution
- **FR5.4**: Help tooltips and methodology explanations
- **FR5.5**: Responsive design for desktop and mobile browsers

## 4. Non-Functional Requirements

### 4.1 Performance
- **NFR1.1**: Model execution time under 30 seconds for standard scenarios
- **NFR1.2**: Page load time under 5 seconds
- **NFR1.3**: Support for 50+ concurrent users
- **NFR1.4**: Poll data refresh within 24 hours of publication

### 4.2 Usability
- **NFR2.1**: Intuitive interface requiring no technical expertise
- **NFR2.2**: Clear error messages and validation feedback
- **NFR2.3**: Accessible design following WCAG 2.1 AA standards
- **NFR2.4**: Mobile-responsive layout

### 4.3 Reliability
- **NFR3.1**: 99% uptime target (within free tier limitations)
- **NFR3.2**: Graceful handling of data source failures
- **NFR3.3**: Automatic fallback to cached data when APIs unavailable
- **NFR3.4**: Error logging and monitoring

### 4.4 Security
- **NFR4.1**: No user authentication required (public application)
- **NFR4.2**: Input validation for all user parameters
- **NFR4.3**: Protection against injection attacks
- **NFR4.4**: HTTPS encryption for all communications

## 5. Data Requirements

### 5.1 Polling Data
- **Source**: Wikipedia UK opinion polling pages, YouGov open data, individual pollster websites
- **Format**: CSV files with standardized schema
- **Update Frequency**: Daily automated scraping
- **Required Fields**: Date, pollster, sample size, Conservative %, Labour %, Liberal Democrat %, SNP %, Others %
- **Retention**: 2 years of historical data

### 5.2 Constituency Data
- **Source**: UK Electoral Commission, ONS Census data
- **Format**: CSV files with constituency identifiers
- **Required Fields**: Constituency name, region, demographic breakdowns, 2019 results
- **Update Frequency**: Static between elections, updated post-boundary changes

### 5.3 Demographic Data
- **Sources**: ONS Census, Brexit referendum results, socioeconomic indices
- **Granularity**: Westminster constituency level
- **Key Variables**: Age distribution, income quartiles, education levels, urban/rural classification, Brexit vote share

## 6. Implementation Plan

### 6.1 Phase 1: Core Infrastructure (Weeks 1-2)
- Set up development environment and repository
- Implement basic Streamlit application structure
- Create data ingestion pipeline for polling data
- Develop constituency clustering algorithm
- Write unit tests for core functions

**Deliverables:**
- Working Streamlit app with basic UI
- Poll data ingestion from Wikipedia
- K-means clustering implementation
- Test suite with >80% coverage

### 6.2 Phase 2: Modeling Engine (Weeks 3-4)
- Implement swing calculation algorithms
- Develop seat prediction model
- Add demographic weighting system
- Create visualization components
- Integrate all model components

**Deliverables:**
- Complete prediction engine
- Interactive visualizations
- Model validation and testing
- Performance optimization

### 6.3 Phase 3: User Interface (Weeks 5-6)
- Design and implement user controls
- Add real-time parameter adjustment
- Create results display components
- Implement export functionality
- Add help documentation

**Deliverables:**
- Polished user interface
- Export capabilities
- User documentation
- Mobile responsiveness

### 6.4 Phase 4: Deployment and Testing (Week 7)
- Create Docker containerization
- Set up CI/CD pipeline
- Deploy to Streamlit Cloud
- Configure custom domain
- Conduct user acceptance testing

**Deliverables:**
- Production deployment
- Domain configuration
- Performance monitoring
- User feedback integration

### 6.5 Phase 5: Launch and Iteration (Week 8+)
- Public launch
- Monitor usage and performance
- Collect user feedback
- Implement improvements
- Plan future features

## 7. Testing Strategy

### 7.1 Unit Testing
- **Framework**: pytest
- **Coverage Target**: >80% code coverage
- **Focus Areas**: Clustering algorithms, swing calculations, data processing functions
- **Test Data**: Synthetic datasets and historical election data

### 7.2 Integration Testing
- **API Integration**: Test all data source connections
- **Model Pipeline**: End-to-end testing of prediction workflow
- **UI Components**: Streamlit component interaction testing

### 7.3 User Acceptance Testing
- **Target Group**: Political analysts and interested users
- **Scenarios**: Common use cases and edge cases
- **Feedback Collection**: In-app feedback forms and user interviews

## 8. Risk Management

### 8.1 Technical Risks
- **Risk**: Free tier hosting limitations
  - **Mitigation**: Monitor usage, prepare paid tier upgrade
- **Risk**: Data source API changes or failures
  - **Mitigation**: Multiple data sources, local caching, manual backup procedures
- **Risk**: Model accuracy concerns
  - **Mitigation**: Validate against historical elections, display confidence intervals

### 8.2 Business Risks
- **Risk**: Low user adoption
  - **Mitigation**: Social media promotion, political community engagement
- **Risk**: Hosting costs exceeding budget
  - **Mitigation**: Usage monitoring, cost-effective hosting alternatives

## 9. Success Metrics

### 9.1 Technical Metrics
- Application uptime >99%
- Average response time <5 seconds
- Model execution time <30 seconds
- Zero critical security vulnerabilities

### 9.2 User Metrics
- 1000+ unique visitors in first month
- Average session duration >5 minutes
- User return rate >20%
- Positive user feedback score >4/5

## 10. Future Enhancements

### 10.1 Short-term (3-6 months)
- Historical election data comparison
- Advanced demographic modeling
- Social media integration for sharing predictions
- Email subscription for prediction updates

### 10.2 Long-term (6-12 months)
- Machine learning model improvements
- Real-time polling data integration
- Multi-election support (local elections, European elections)
- Advanced statistical modeling techniques

## 11. Budget Estimation

### 11.1 Development Costs
- Domain registration: £10/year
- Development time: 8 weeks (self-developed)
- Third-party services: £0 (free tiers)

### 11.2 Operational Costs (Annual)
- Hosting: £0 (Streamlit Cloud free tier)
- Domain renewal: £10
- Monitoring tools: £0 (free tiers)
- **Total Annual Cost**: £10

### 11.3 Scaling Costs
- Streamlit Cloud Pro: $20/month (if needed)
- Additional data sources: $0-50/month
- Enhanced hosting: $50-200/month (if required)

## 12. Conclusion

The UK Election Simulator represents a focused, technically achievable project that delivers significant value to users interested in UK political analysis. By leveraging Streamlit's rapid development capabilities and free hosting options, the project can be delivered quickly and cost-effectively while maintaining professional quality and functionality.

The modular architecture allows for future enhancements and scaling, while the comprehensive testing strategy ensures reliability and accuracy. The project's success will be measured through both technical performance metrics and user engagement indicators.