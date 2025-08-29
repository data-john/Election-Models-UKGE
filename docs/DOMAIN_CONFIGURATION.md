# Domain Configuration Guide: electionmodels.com/UKGE

## Overview
You own `electionmodels.com` and want `electionmodels.com/UKGE` to point to your Streamlit Cloud app.

## Important: Streamlit Cloud Domain Limitations

### Current Streamlit Cloud Behavior
- **Subdomain Support**: ✅ Supports custom subdomains (e.g., `ukge.electionmodels.com`)
- **Path-based Routing**: ❌ Does NOT support custom paths (e.g., `electionmodels.com/UKGE`)

### Recommended Solution Options

## Option 1: Subdomain Approach (Recommended) ⭐
Use `ukge.electionmodels.com` instead of `electionmodels.com/UKGE`

### DNS Configuration
1. **In your domain provider's DNS settings:**
   ```
   Type: CNAME
   Name: ukge
   Target: [Your Streamlit App URL]
   TTL: 300 (5 minutes)
   ```

2. **In Streamlit Cloud Dashboard:**
   - Go to your app settings
   - Navigate to "General" → "Custom domain"
   - Enter: `ukge.electionmodels.com`
   - Save configuration

### Benefits
- ✅ Full Streamlit Cloud support
- ✅ Automatic SSL certificates
- ✅ Easy to remember URL
- ✅ Professional subdomain structure

## Option 2: Redirect Solution (Path-based)
Keep `electionmodels.com/UKGE` using redirects

### Implementation Steps

#### Step 1: Deploy App with Subdomain
1. Deploy app to Streamlit Cloud first
2. Configure subdomain: `ukge.electionmodels.com` (as in Option 1)

#### Step 2: Set Up Redirect Server
Create a simple redirect server for your main domain:

**Create `/redirect/index.html`:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Election Models - Redirecting...</title>
    <script>
        // Check if URL contains /UKGE and redirect
        if (window.location.pathname.includes('/UKGE')) {
            window.location.replace('https://ukge.electionmodels.com');
        }
    </script>
    <meta http-equiv="refresh" content="0;url=https://ukge.electionmodels.com">
</head>
<body>
    <p>Redirecting to <a href="https://ukge.electionmodels.com">UK General Election Models</a>...</p>
</body>
</html>
```

#### Step 3: Host Main Domain
1. **Use GitHub Pages, Netlify, or Vercel** to host the redirect
2. **Configure DNS** for main domain to point to hosting service
3. **Set up redirect rules** in hosting service for `/UKGE` → subdomain

### Example with Netlify
1. **Deploy redirect site to Netlify**
2. **Create `_redirects` file:**
   ```
   /UKGE/* https://ukge.electionmodels.com/:splat 301
   /UKGE https://ukge.electionmodels.com 301
   ```
3. **Point `electionmodels.com` DNS to Netlify**

## Option 3: Reverse Proxy (Advanced)
Use a reverse proxy server to handle path routing

### Requirements
- VPS or cloud server (DigitalOcean, AWS, etc.)
- Nginx or Apache configuration
- SSL certificate management

### Nginx Configuration Example
```nginx
server {
    listen 443 ssl;
    server_name electionmodels.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location /UKGE {
        proxy_pass https://your-streamlit-app.streamlit.app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Remove /UKGE from path when forwarding
        rewrite ^/UKGE(.*)$ $1 break;
    }
    
    location / {
        # Your main website content
        root /var/www/electionmodels.com;
        index index.html;
    }
}
```

## Recommended Implementation Plan

### Phase 1: Quick Deployment (Recommended Start) 🚀
1. **Deploy to Streamlit Cloud** with subdomain approach
2. **Configure**: `ukge.electionmodels.com`
3. **Test and verify** functionality
4. **Update documentation** and links

### Phase 2: Optional Path Routing (If needed)
1. **Keep subdomain working** (don't break what works)
2. **Add redirect solution** for `electionmodels.com/UKGE`
3. **Test both URLs work**

## Step-by-Step Implementation (Option 1 - Recommended)

### Step 1: Get Streamlit App URL
1. **Check your Streamlit Cloud dashboard**
2. **Note the app URL** (something like `election-simulator.streamlit.app`)

### Step 2: Configure DNS
1. **Log into your domain provider** (GoDaddy, Namecheap, Cloudflare, etc.)
2. **Go to DNS management**
3. **Add CNAME record:**
   ```
   Type: CNAME
   Name: ukge
   Target: election-simulator.streamlit.app
   TTL: 300
   ```

### Step 3: Configure Streamlit Cloud
1. **Go to Streamlit Cloud dashboard**
2. **Select your app**
3. **Settings** → **General** → **Custom domain**
4. **Enter**: `ukge.electionmodels.com`
5. **Save changes**

### Step 4: Wait for Propagation
- **DNS propagation**: 5 minutes to 24 hours
- **SSL certificate**: Automatic (15-30 minutes after DNS)

### Step 5: Test and Verify
1. **Test URL**: `https://ukge.electionmodels.com`
2. **Check SSL**: Should show secure connection
3. **Test functionality**: Verify app works correctly

## URL Structure Comparison

| Option | URL | Streamlit Support | Complexity | SSL |
|--------|-----|-------------------|------------|-----|
| **Subdomain** | `ukge.electionmodels.com` | ✅ Full | 🟢 Low | ✅ Auto |
| **Redirect** | `electionmodels.com/UKGE` → subdomain | ⚠️ Redirect | 🟡 Medium | ✅ Manual |
| **Reverse Proxy** | `electionmodels.com/UKGE` | ✅ Direct | 🔴 High | ✅ Manual |

## Troubleshooting

### Common Issues
1. **DNS not propagating**: Wait up to 24 hours, check with `nslookup ukge.electionmodels.com`
2. **SSL certificate pending**: Wait 30 minutes after DNS propagation
3. **App not loading**: Verify Streamlit app is deployed and running
4. **Custom domain not accepted**: Check domain spelling and DNS configuration

### Verification Commands
```bash
# Check DNS propagation
nslookup ukge.electionmodels.com

# Check SSL certificate
curl -I https://ukge.electionmodels.com

# Test redirect (if using Option 2)
curl -I https://electionmodels.com/UKGE
```

## Next Steps
1. **Choose your preferred option** (I recommend Option 1: Subdomain)
2. **Follow the step-by-step implementation**
3. **Update your project documentation** with the final URL
4. **Test thoroughly** before announcing

---

**Created**: Sprint 1 Day 4 (29 August 2025)  
**For**: electionmodels.com domain configuration  
**Recommended**: Option 1 (Subdomain approach)
