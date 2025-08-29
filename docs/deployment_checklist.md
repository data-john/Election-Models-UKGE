# Sprint 1 Day 4 - Streamlit Cloud Deployment Checklist

## ✅ Pre-Deployment Complete (Automated)
- [x] All deployment configuration files created
- [x] Streamlit Cloud configuration ready (.streamlit/config.toml)
- [x] Secrets template prepared (.streamlit/secrets.toml) 
- [x] System packages configured (packages.txt)
- [x] Deployment documentation complete (docs/DEPLOYMENT.md)
- [x] Verification script passing (scripts/verify_deployment_readiness.py)
- [x] README updated with deployment information
- [x] All changes committed to Sprint1 branch

## 📋 Manual Deployment Steps (Ready to Execute)

### Step 1: Repository Preparation
- [ ] Merge Sprint1 branch to main
- [ ] Verify main branch has all changes
- [ ] Confirm application runs locally on main branch

### Step 2: Streamlit Cloud Configuration
- [ ] Visit [share.streamlit.io](https://share.streamlit.io)
- [ ] Connect GitHub account and repository
- [ ] Select repository: `Election-Models-UKGE`
- [ ] Set branch: `main`
- [ ] Set main file path: `src/app.py`
- [ ] Set Python version: 3.11

### Step 3: Application Deployment
- [ ] Deploy application (automatic after configuration)
- [ ] Wait for build completion (~2-5 minutes)
- [ ] Verify application loads without errors
- [ ] Test basic functionality (poll table display)

### Step 4: Secrets Configuration
- [ ] Access App Settings → Secrets in Streamlit Cloud dashboard
- [ ] Copy content from `.streamlit/secrets.toml`
- [ ] Replace placeholder values with production settings
- [ ] Save secrets configuration

### Step 5: Custom Domain Setup
- [ ] In Streamlit Cloud: Settings → General → Custom domain
- [ ] Enter domain: `www.electionmodels.com`
- [ ] Set path: `/UKGE`
- [ ] Note the CNAME target provided by Streamlit
- [ ] Configure DNS with domain provider:
  - Type: CNAME
  - Name: www.electionmodels.com
  - Target: [Streamlit provided CNAME]
  - TTL: 300 (5 minutes)

### Step 6: Production Verification
- [ ] Test application at Streamlit-provided URL
- [ ] Verify all functionality works in production
- [ ] Check mobile responsiveness
- [ ] Test error handling
- [ ] Monitor application logs for issues

### Step 7: Domain Verification (24-48 hours)
- [ ] Wait for DNS propagation
- [ ] Test domain accessibility: www.electionmodels.com/UKGE
- [ ] Verify SSL certificate is active (HTTPS)
- [ ] Confirm redirects work properly
- [ ] Update documentation with live URLs

## 🔧 Troubleshooting Quick Reference

### Common Issues
1. **Build Failures**: Check requirements.txt for package conflicts
2. **Import Errors**: Verify all packages in requirements.txt
3. **Path Issues**: Ensure main file path is exactly `src/app.py`
4. **Domain Issues**: DNS propagation takes 24-48 hours
5. **SSL Issues**: SSL certificates auto-provision after domain verification

### Health Check URLs
- **Streamlit URL**: [Generated after deployment]
- **Custom Domain**: www.electionmodels.com/UKGE (after DNS propagation)
- **Health Endpoint**: [domain]/health (built into application)

### Support Resources
- **Streamlit Cloud Docs**: https://docs.streamlit.io/streamlit-cloud
- **DNS Troubleshooting**: Use `nslookup` or online DNS checkers
- **Application Logs**: Available in Streamlit Cloud dashboard

## 📊 Success Criteria
- [ ] Application accessible via Streamlit Cloud URL
- [ ] No errors in production logs
- [ ] All major features functional (poll table, filtering, charts)
- [ ] Mobile-responsive design working
- [ ] Custom domain configured (DNS propagation pending)
- [ ] SSL certificate active
- [ ] Deployment documentation updated with live URLs

---

**Prepared**: Sprint 1 Day 4 (29 August 2025)
**Ready for**: Manual deployment execution
**Estimated Time**: 30-45 minutes (excluding DNS propagation)
**Dependencies**: GitHub account, Domain management access
