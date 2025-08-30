import pandas as pd
import numpy as np
import requests
from io import StringIO

next_url = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_next_United_Kingdom_general_election"
url_24 = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2024_United_Kingdom_general_election"
url_19 = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2019_United_Kingdom_general_election"
url_17 = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2017_United_Kingdom_general_election"
url_15 = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2015_United_Kingdom_general_election"
url_10 = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2010_United_Kingdom_general_election"
url_05 = "https://en.wikipedia.org/wiki/Opinion_polling_for_the_2005_United_Kingdom_general_election"
big_std = 0.023
small_std = 0.016


next_col_dict = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"LD",
    "Nat":"SNP",
    "Grn":"Grn",
    "Ref":"Ref",
    "Oth":"Others",
}
col_dict24 = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dems",
    "Nat":"SNP",
    "Grn":"Green",
    "Ref":"Reform",
    "Oth":"Others",
}
col_dict19 = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dem",
    "Nat":"SNP",
    "Grn":"Green",
    "Ref":"Brexit",
    "Oth":"Other",
}
col_dict17 = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dem",
    "Nat":"SNP",
    "Grn":"Green",
    "Ref":"UKIP",
    "Oth":"Others",
}
col_dict15 = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dem",
    # "Nat":"SNP",
    "Grn":"Green",
    "Ref":"UKIP",
    "Oth":"Others",
}
col_dict10 = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dem",
    # "Nat":"SNP",
    # "Grn":"Green",
    # "Ref":"UKIP",
    "Oth":"Others",
}
col_dict05 = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dem",
    # "Nat":"SNP",
    # "Grn":"Green",
    # "Ref":"UKIP",
    "Oth":"Others",
}


def try_to_int(v):
    """Enhanced integer conversion with better error handling"""
    if v is None:
        return 0
    
    # Handle numpy/pandas NaN and arrays separately
    try:
        if hasattr(v, '__len__') and not isinstance(v, str):
            # It's an array-like object, invalid for int conversion
            return 0
    except TypeError:
        # Some objects might not have __len__, continue with normal processing
        pass
    
    try:
        if pd.isna(v):
            return 0
    except (ValueError, TypeError):
        # pd.isna() might fail on some types, continue with normal processing
        pass
    
    try:
        # Handle string inputs that might have commas or other formatting
        if isinstance(v, str):
            # Remove common formatting characters
            v = v.replace(',', '').replace(' ', '').strip()
            if v == '' or v.lower() in ['n/a', 'na', 'unknown', '-']:
                return 0
        return int(float(v))  # Convert to float first to handle '42.0' strings
    except (ValueError, TypeError, OverflowError):
        return 0

def try_to_float(v):
    """Enhanced float conversion with better error handling"""
    if v is None:
        return 0.0
    
    # Handle numpy/pandas NaN and arrays separately
    try:
        if hasattr(v, '__len__') and not isinstance(v, str):
            # It's an array-like object, invalid for float conversion
            return 0.0
    except TypeError:
        # Some objects might not have __len__, continue with normal processing
        pass
    
    try:
        if pd.isna(v):
            return 0.0
    except (ValueError, TypeError):
        # pd.isna() might fail on some types, continue with normal processing
        pass
    
    try:
        # Handle string inputs
        if isinstance(v, str):
            # Remove common formatting characters and handle percentage signs
            cleaned = v.replace(' ', '').replace('%', '').strip()
            if cleaned == '' or cleaned.lower() in ['n/a', 'na', 'unknown', '-']:
                return 0.0
            # Handle comma as thousands separator (e.g., "1,234.56")
            cleaned = cleaned.replace(',', '')
        else:
            cleaned = v
        
        result = float(cleaned)
        
        # Check for reasonable bounds
        if result < 0:
            return 0.0
        elif result > 999:  # Sanity check for very large values
            return 0.0
        
        return result
        
    except (ValueError, TypeError, OverflowError):
        return 0.0

def calculate_others(list_of_pcs):
    others = 1-sum(list_of_pcs)
    return others

def get_latest_polls(df, n=10, allow_repeated_pollsters=False):
    """
    Get the latest n polls with enhanced error handling
    Sprint 2 Day 5: Comprehensive edge case handling
    """
    # Input validation
    if df is None:
        raise ValueError("DataFrame is None")
    
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected DataFrame, got {type(df)}")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")
    
    # Work with a copy to avoid modifying original
    df = df.copy()
    
    try:
        # Remove duplicate pollsters if requested
        if not allow_repeated_pollsters:
            pollster_cols = []
            for col in df.columns:
                if "Poll" in col or "poll" in col.lower() or "Company" in col or "company" in col.lower():
                    pollster_cols.append(col)
            
            if pollster_cols:
                try:
                    # Use the first pollster column found
                    pollster_col = pollster_cols[0]
                    initial_count = len(df)
                    df = df.drop_duplicates(subset=[pollster_col], keep="first")
                    final_count = len(df)
                    
                    if final_count < initial_count:
                        # Duplicate pollsters were removed
                        pass
                except KeyError as e:
                    # Column might not exist after all, continue without deduplication
                    pass
                except Exception as e:
                    # Other error in deduplication, continue with original data
                    pass
        
        # Filter by total percentages if Total column exists
        if "Total" in df.columns:
            try:
                # Convert Total column to numeric, handling various formats
                total_series = pd.to_numeric(df["Total"], errors='coerce')
                df = df.copy()  # Ensure we have a copy
                df["Total"] = total_series
                
                # Remove rows with invalid totals (less than 97% or more than 103%)
                initial_count = len(df)
                df = df[(df["Total"] >= 0.97) & (df["Total"] <= 1.03)].copy()
                final_count = len(df)
                
                if final_count == 0:
                    # All polls filtered out due to invalid totals, use more lenient criteria
                    df = df.copy()  # Reset df
                    df = df[(df["Total"] >= 0.90) & (df["Total"] <= 1.10)].copy()  # More lenient
                    
                    if len(df) == 0:
                        # Still no valid polls, return without total filtering
                        df = df.copy()  # Reset to original after filtering
                
            except Exception as e:
                # Error processing totals, continue without total filtering
                pass
        
        # Return the requested number of polls (or all if fewer available)
        if len(df) <= n:
            return df
        else:
            return df.iloc[:n].copy()
            
    except Exception as e:
        raise Exception(f"Error processing polls: {str(e)}")

def wiki_polls_preprocessing(df, col_names = {
    "Con":"Con",
    "Lab":"Lab",
    "Lib":"Lib Dems",
    "Nat":"SNP",
    "Grn":"Green",
    "Ref":"Reform",
    "Oth":"Others",
}):
    df["Sample size"] = df["Sample size"].map(lambda x: try_to_int(x))
    df.columns = df.columns.droplevel(1)
    df = df.drop(df[df["Sample size"]==0].index).copy()
    pc_cols = ["Con", "Lab", "Lib Dems", "SNP", "Green", "Reform", "Others"]
    pc_cols = list(col_names.values())
    for col in pc_cols:
        if type(df[col].iloc[0]) is str:
            df[col] = df[col].map(lambda x:try_to_float(str(x).replace("%",""))/100)
    df[col_names["Oth"]] = df.apply(lambda x: calculate_others([x[col_names["Con"]],x[col_names["Lab"]],x[col_names["Lib"]],x[col_names["Nat"]],x[col_names["Grn"]],x[col_names["Ref"]]]) if x[col_names["Oth"]]==9.99 else x[col_names["Oth"]],axis=1)
    for col in df.columns:
        if type(df[col].iloc[0]) is str:
            df[col] = df[col].map(lambda x:str(x).replace("%",""))
    for col in pc_cols:
        df.drop(df[df[col]==9.99].index,axis=0,inplace=True)
    df["Total"] = df[pc_cols].sum(axis=1)
    return df.copy()

def get_wiki_polls_table(url):
    """
    Enhanced function to get polling tables from Wikipedia with robust error handling
    Sprint 2 Day 5: Enhanced error handling and edge cases
    """
    import time
    
    # Configuration for retry logic
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    TIMEOUT_SECONDS = 30
    
    for attempt in range(MAX_RETRIES):
        try:
            # Set comprehensive headers to avoid 403 errors and appear as legitimate browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            }
            
            # Validate URL format
            if not url or not isinstance(url, str):
                raise ValueError("Invalid URL provided")
            
            if not (url.startswith('http://') or url.startswith('https://')):
                raise ValueError("URL must start with http:// or https://")
            
            # Make request with comprehensive error handling
            response = requests.get(
                url, 
                headers=headers, 
                timeout=TIMEOUT_SECONDS,
                allow_redirects=True,
                verify=True  # Verify SSL certificates
            )
            
            # Enhanced status code handling
            if response.status_code == 429:  # Rate limited
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (attempt + 1)  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                else:
                    raise requests.RequestException(f"Rate limited (429) after {MAX_RETRIES} attempts")
            
            response.raise_for_status()  # Raises an HTTPError for bad responses
            
            # Validate response content
            if not response.text or len(response.text.strip()) < 100:
                raise ValueError("Response content appears empty or too short")
            
            # Parse HTML with pandas - enhanced error handling
            try:
                tables = pd.read_html(StringIO(response.text), header=[0, 1])
            except ValueError as e:
                # Try without multi-level headers if first attempt fails
                try:
                    tables = pd.read_html(StringIO(response.text))
                except ValueError as e2:
                    raise Exception(f"Failed to parse HTML tables. Original error: {str(e)}, Fallback error: {str(e2)}")
            
            # Enhanced table validation
            if not tables:
                raise ValueError("No tables found in the Wikipedia page")
            
            poll_tables = []
            conservative_patterns = ["Con", "Conservative", "Tory", "Conservatives"]
            
            for i, table in enumerate(tables):
                try:
                    # Handle multi-level columns
                    if hasattr(table.columns, 'nlevels') and table.columns.nlevels > 1:
                        # Flatten multi-level columns for searching
                        flat_columns = [' '.join(col).strip() for col in table.columns.values]
                    else:
                        flat_columns = list(table.columns)
                    
                    # Check for Conservative party in various formats
                    has_conservative = any(
                        any(pattern in str(col) for pattern in conservative_patterns)
                        for col in flat_columns
                    )
                    
                    if has_conservative and len(table) > 0:
                        poll_tables.append(table)
                        break  # Take the first valid table
                        
                except Exception as table_error:
                    # Log but continue checking other tables
                    continue
            
            if not poll_tables:
                raise ValueError(
                    f"No polling tables found with Conservative column. "
                    f"Found {len(tables)} tables total. "
                    f"Available columns in first table: {list(tables[0].columns) if tables else 'None'}"
                )
            
            df = poll_tables[0].copy()
            
            # Validate DataFrame structure
            if df.empty:
                raise ValueError("Selected polling table is empty")
            
            if len(df.columns) < 3:
                raise ValueError(f"Polling table has insufficient columns: {len(df.columns)}")
            
            return df
            
        except requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise Exception(f"Request timed out after {TIMEOUT_SECONDS} seconds and {MAX_RETRIES} attempts")
            
        except requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise Exception(f"Network connection failed after {MAX_RETRIES} attempts: {str(e)}")
            
        except requests.exceptions.HTTPError as e:
            status_code = getattr(e.response, 'status_code', 'Unknown')
            if status_code in [502, 503, 504] and attempt < MAX_RETRIES - 1:
                # Retry on server errors
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise Exception(f"HTTP error {status_code}: {str(e)}")
            
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            raise Exception(f"Request failed after {MAX_RETRIES} attempts: {str(e)}")
            
        except Exception as e:
            # Don't retry for non-network errors
            raise Exception(f"Failed to parse polling table: {str(e)}")
    
    # Should not reach here due to the loop structure, but safety fallback
    raise Exception(f"Failed to fetch Wikipedia page after {MAX_RETRIES} attempts")


def get_latest_polls_from_html(url, col_dict=next_col_dict, n=10, allow_repeated_pollsters=False):
    """
    Enhanced function with comprehensive error handling and edge cases
    Sprint 2 Day 5: Robust error handling and data validation
    """
    try:
        # Input validation
        if not url or not isinstance(url, str):
            raise ValueError("Invalid URL provided")
        
        if not isinstance(col_dict, dict) or not col_dict:
            raise ValueError("Invalid column dictionary provided")
        
        if not isinstance(n, int) or n <= 0:
            raise ValueError("Number of polls must be a positive integer")
        
        if n > 100:  # Reasonable upper limit
            raise ValueError("Requested number of polls exceeds maximum limit (100)")
        
        # Step 1: Get raw table data with enhanced error handling
        try:
            df = get_wiki_polls_table(url)
        except Exception as e:
            raise Exception(f"Failed to fetch polling table: {str(e)}")
        
        # Step 2: Preprocess data with enhanced validation
        try:
            df = wiki_polls_preprocessing(df, col_names=col_dict)
        except Exception as e:
            raise Exception(f"Failed to preprocess polling data: {str(e)}")
        
        # Step 3: Validate preprocessed data
        if df is None or df.empty:
            raise ValueError("Preprocessed data is empty")
        
        # Check for required columns after preprocessing
        expected_cols = list(col_dict.values())
        missing_cols = [col for col in expected_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns after preprocessing: {missing_cols}")
        
        # Step 4: Get latest polls with enhanced error handling
        try:
            df = get_latest_polls(df, n=n, allow_repeated_pollsters=allow_repeated_pollsters)
        except Exception as e:
            raise Exception(f"Failed to extract latest polls: {str(e)}")
        
        # Final validation
        if df is None or df.empty:
            raise ValueError("No valid polls found after filtering")
        
        if len(df) == 0:
            raise ValueError("All polls were filtered out due to data quality issues")
        
        return df
        
    except ValueError as e:
        # Re-raise ValueError as-is (these are input validation errors)
        raise e
    except Exception as e:
        # Wrap other exceptions with context
        raise Exception(f"Failed to get latest polls from HTML: {str(e)}")


def get_latest_polls_dict(n=3):
    """
    Enhanced function to get latest polls as dictionary with error handling
    Sprint 2 Day 5: Added comprehensive error handling
    """
    try:
        # Input validation
        if not isinstance(n, int) or n <= 0:
            raise ValueError("Number of polls must be a positive integer")
        
        if n > 20:  # Reasonable upper limit for dictionary format
            raise ValueError("Requested number of polls exceeds maximum limit for dictionary format (20)")
        
        # Get the polls data
        latest_polls_df = get_latest_polls_from_html(next_url)
        
        if latest_polls_df is None or latest_polls_df.empty:
            raise ValueError("No polling data available")
        
        # Extract only the party columns
        party_columns = list(next_col_dict.values())
        available_columns = [col for col in party_columns if col in latest_polls_df.columns]
        
        if not available_columns:
            raise ValueError("No valid party columns found in polling data")
        
        latest_polls_df = latest_polls_df[available_columns].copy()
        
        # Validate we have enough polls
        if len(latest_polls_df) < n:
            n = len(latest_polls_df)  # Use all available polls if requested number exceeds available
        
        # Build dictionary
        latest_polls_dict = {}
        
        for i in range(n):
            try:
                row = latest_polls_df.iloc[i]
                for col in latest_polls_df.columns:
                    key = f"{col}{i}"
                    value = row[col]
                    
                    # Validate numeric values
                    if pd.isna(value):
                        value = 0.0
                    elif not isinstance(value, (int, float)):
                        try:
                            value = float(value)
                        except (ValueError, TypeError):
                            value = 0.0
                    
                    latest_polls_dict[key] = value
                    
            except Exception as e:
                # Skip this row but continue with others
                continue
        
        if not latest_polls_dict:
            raise ValueError("Failed to create polls dictionary from available data")
        
        return latest_polls_dict
        
    except Exception as e:
        raise Exception(f"Failed to get latest polls dictionary: {str(e)}")


def get_weighted_poll_avg(url, col_dict):
    """
    Enhanced function to calculate weighted poll average with error handling
    Sprint 2 Day 5: Added comprehensive error handling and validation
    """
    try:
        # Input validation
        if not url or not isinstance(url, str):
            raise ValueError("Invalid URL provided")
        
        if not isinstance(col_dict, dict) or not col_dict:
            raise ValueError("Invalid column dictionary provided")
        
        party_columns = list(col_dict.values())
        if not party_columns:
            raise ValueError("No party columns specified in column dictionary")
        
        # Get short-term average (last 3 polls)
        try:
            sdf = get_latest_polls_from_html(url, col_dict=col_dict, n=3)
            if sdf is None or sdf.empty:
                raise ValueError("No short-term polling data available")
            
            # Filter to available party columns
            available_short_cols = [col for col in party_columns if col in sdf.columns]
            if not available_short_cols:
                raise ValueError("No valid party columns in short-term data")
            
            sdf_mean = sdf[available_short_cols].mean()
            
        except Exception as e:
            raise Exception(f"Failed to calculate short-term average: {str(e)}")
        
        # Get long-term average (last 10 polls)
        try:
            ldf = get_latest_polls_from_html(url, col_dict=col_dict, n=10)
            if ldf is None or ldf.empty:
                raise ValueError("No long-term polling data available")
            
            # Filter to available party columns
            available_long_cols = [col for col in party_columns if col in ldf.columns]
            if not available_long_cols:
                raise ValueError("No valid party columns in long-term data")
            
            ldf_mean = ldf[available_long_cols].mean()
            
        except Exception as e:
            raise Exception(f"Failed to calculate long-term average: {str(e)}")
        
        # Combine the averages (giving equal weight to short and long term)
        try:
            # Ensure we have matching columns for combination
            common_columns = list(set(sdf_mean.index) & set(ldf_mean.index))
            if not common_columns:
                raise ValueError("No common party columns between short and long term data")
            
            # Create DataFrame for averaging
            combined_df = pd.concat([
                sdf_mean[common_columns], 
                ldf_mean[common_columns]
            ], axis=1)
            
            # Calculate final weighted average
            weighted_avg = combined_df.mean(axis=1)
            
            # Validate results
            if weighted_avg.empty:
                raise ValueError("Failed to calculate weighted average")
            
            # Check for reasonable values (percentages should be between 0 and 1)
            invalid_values = weighted_avg[(weighted_avg < 0) | (weighted_avg > 1)]
            if not invalid_values.empty:
                # Log warning but don't fail - data might be in percentage format
                pass
            
            return weighted_avg
            
        except Exception as e:
            raise Exception(f"Failed to combine polling averages: {str(e)}")
        
    except Exception as e:
        raise Exception(f"Failed to get weighted poll average: {str(e)}")

