## ✅ I1 - RESOLVED
~~Polling data dates are all showing as the same date:~~

~~2025-08-30	BMG Research[2]~~
~~2025-08-30	Find Out Now[3]~~
~~2025-08-30	YouGov[4]~~
~~2025-08-30	Opinium[5]~~

**Resolution:** Fixed Wikipedia date parsing in `format_poll_data_for_display()` function. The issue was caused by improper parsing of Wikipedia date formats like "26–28 Aug". Added proper Wikipedia date parser that:
- Handles date ranges (takes end date)
- Adds current year to incomplete dates
- Handles year rollover for future dates
- Now correctly shows: 2025-08-28 (2 days ago), 2025-08-27 (3 days ago), etc.

## ✅ I2 - RESOLVED  
~~Streamlit deprecation~~
~~Streamlit API Compatibility: Updated all st.dataframe() calls from width='stretch' to use_container_width=True~~
~~A warning has said that use_container_width=True is going to be deprecated~~

**Resolution:** Updated all `st.dataframe()` calls to use `width=None` instead of the deprecated `use_container_width=True` parameter. This addresses Streamlit API deprecation warnings and ensures future compatibility.

## I3 
The colours in the Polling Average Trend graph don't match the party colours of the cards above

## I4
Only on deployed version, error on app:
📋 Recent Polling Data
❌ Application Error: Invalid width value: None. Width must be either an integer (pixels), 'stretch', or 'content'.
If this error persists, please refresh the page or contact support.
Attempting to load minimal data...

Unable to load any data. Please refresh the page.

Error details: Invalid width value: None. Width must be either an integer (pixels), 'stretch', or 'content'.

## I5
Pollsters names appear with a ref number from Wikpedia, this should be stripped.
Find Out Now[3]
Find Out Now[6]
Lord Ashcroft Polls[10][a]
Find Out Now[11]
YouGov[12]
Find Out Now[15]