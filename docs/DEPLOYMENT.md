# Streamlit Cloud Deployment Configuration
# UK Election Simulator

## Application Details
- **App Name**: UK Election Simulator
- **Repository**: Election-Models-UKGE
- **Main Branch**: main
- **App File**: src/app.py
- **Python Version**: 3.11

## Deployment Settings

### Basic Configuration
```
Main file path: src/app.py
Requirements file: requirements.txt
Python version: 3.11
```

### Advanced Settings
```
System packages: packages.txt
Streamlit config: .streamlit/config.toml
Secrets: .streamlit/secrets.toml (configure in dashboard)
```

## Domain Configuration

### Primary Domain
- **Target URL**: www.electionmodels.com/UKGE
- **Streamlit URL**: [to be configured after deployment]

### DNS Setup Required
1. Create CNAME record pointing to Streamlit Cloud
2. Configure custom domain in Streamlit Cloud dashboard
3. Update SSL certificate settings

## Environment Variables / Secrets

### Production Secrets (Configure in Streamlit Cloud Dashboard)
```toml
[general]
app_environment = "production"
debug_mode = false

[database]
# Future database connections

[api]  
# Future API keys
```

## Deployment Checklist

### Pre-Deployment
- [ ] All code committed to main branch
- [ ] Requirements.txt up to date
- [ ] App runs locally without errors
- [ ] Docker container tested (Sprint 1 Day 3)
- [ ] Health checks passing

### Streamlit Cloud Setup
- [ ] Connect GitHub repository
- [ ] Configure main file path: `src/app.py`
- [ ] Set Python version: 3.11
- [ ] Upload secrets configuration
- [ ] Enable auto-deploy on main branch updates

### Domain Configuration  
- [ ] Choose domain approach: subdomain vs path-based (see DOMAIN_CONFIGURATION.md)
- [ ] **Recommended**: Configure subdomain: ukge.electionmodels.com
- [ ] **Alternative**: Set up redirect for electionmodels.com/UKGE → subdomain
- [ ] Update DNS settings with CNAME record
- [ ] Configure custom domain in Streamlit Cloud dashboard
- [ ] Verify SSL certificate (automatic with Streamlit Cloud)
- [ ] Test domain accessibility

### Post-Deployment
- [ ] Smoke test all major features
- [ ] Verify mobile responsiveness
- [ ] Check error handling
- [ ] Monitor resource usage
- [ ] Update documentation

## Deployment URL (Free Tier)
- Your app is available at: **https://election-simulator.streamlit.app**
- Custom domains (e.g., electionmodels.com) are NOT supported on the free tier.
- Share the Streamlit Cloud URL with users.

## Custom Domain (Paid Plans Only)
- If you upgrade, see DOMAIN_CONFIGURATION.md for setup instructions.

## Troubleshooting

### Common Issues
1. **Import Errors**: Check requirements.txt for missing packages
2. **Path Issues**: Ensure all file paths are relative to repository root
3. **Memory Issues**: Monitor Streamlit Cloud resource usage
4. **Domain Issues**: Verify DNS propagation (can take 24-48 hours)
5. **packages.txt Format Error**: 
   - ❌ **Issue**: `E: Unable to locate package #` errors during deployment
   - ✅ **Solution**: Remove all comments from packages.txt - only package names, one per line
   - **Note**: Streamlit Cloud treats every line as a package to install

### Health Check Endpoint
The application includes built-in health monitoring accessible at:
- Local: http://localhost:8501/health
- Production: [domain]/health

### Support Resources
- Streamlit Cloud Documentation
- GitHub repository issues
- Application logs in Streamlit Cloud dashboard

---

**Last Updated**: Sprint 1, Day 4 (29 August 2025)
**Next Update**: Post-deployment verification
