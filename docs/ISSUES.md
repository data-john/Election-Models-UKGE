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

## ✅ I3 - RESOLVED
~~The colours in the Polling Average Trend graph don't match the party colours of the cards above~~

**Resolution:** Replaced simple `st.line_chart()` with Altair chart that uses the same party color mapping as the cards above. The Polling Average Trend now displays with consistent colors:
- Conservative: #0087DC (blue)
- Labour: #E4003B (red)  
- Liberal Democrat: #FAA61A (orange)
- Reform UK: #12B6CF (cyan)
- Green: #6AB023 (green)
- SNP: #FDF23B (yellow)

Fixed deprecated Altair API calls (`selection_multi` → `selection_point`, `add_selection` → `add_params`) and simplified chart implementation for better compatibility. Chart now displays correctly with matching party colors and interactive tooltips.

## ✅ I4 - RESOLVED
~~Only on deployed version, error on app:~~
~~📋 Recent Polling Data~~
~~❌ Application Error: Invalid width value: None. Width must be either an integer (pixels), 'stretch', or 'content'.~~
~~If this error persists, please refresh the page or contact support.~~
~~Attempting to load minimal data...~~

~~Unable to load any data. Please refresh the page.~~

~~Error details: Invalid width value: None. Width must be either an integer (pixels), 'stretch', or 'content'.~~

**Resolution:** Fixed all `st.dataframe()` calls that were using `width=None` parameter. Replaced with `use_container_width=True` which is the correct parameter for responsive dataframe display. This fixes the deployment error that was preventing the app from displaying data tables properly.

## ✅ I5 - RESOLVED  
~~Pollsters names appear with a ref number from Wikpedia, this should be stripped.~~
~~Find Out Now[3]~~
~~Find Out Now[6]~~
~~Lord Ashcroft Polls[10][a]~~
~~Find Out Now[11]~~
~~YouGov[12]~~
~~Find Out Now[15]~~

**Resolution:** Implemented `clean_pollster_name()` function that strips Wikipedia reference numbers using regex patterns. The function handles:
- Single numeric references like `[3]`, `[12]`  
- Letter references like `[a]`
- Complex combinations like `[10][a]`
- Edge cases with None, empty strings, pandas NA values

Applied automatically in `format_poll_data_for_display()` so all pollster names are cleaned before display. Examples:
- "Find Out Now[3]" → "Find Out Now"
- "YouGov[12]" → "YouGov"
- "Lord Ashcroft Polls[10][a]" → "Lord Ashcroft Polls"

## I6
Polling Average Trend graph shows multiple averages for the same date in some cases. Only one average should be displayed for each date - the average that includes all the polls from that date should be used.
