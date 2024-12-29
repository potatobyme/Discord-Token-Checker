import requests
import base64
import json
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from colorama import Fore, Style, init
import time
import random
import concurrent.futures

# Initialize colorama for cross-platform support
init(autoreset=True)

# File paths
TOKENS_FILE = "tokens.txt"
VALID_TOKENS_FILE = "valid_tokens.txt"
INVALID_TOKENS_FILE = "invalid_tokens.txt"

# Discord API URL for token validation
DISCORD_API = "https://discord.com/api/v10/users/@me"

# Comprehensive set of User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1",
]

# Function to convert Snowflake ID to timestamp
def snowflake_to_timestamp(snowflake):
    """Converts a Snowflake ID to a timestamp (in UTC)."""
    snowflake = int(snowflake)
    timestamp = (snowflake >> 22) + 1420070400000  # Discord's epoch starts from 2015-01-01
    return datetime.fromtimestamp(timestamp / 1000, timezone.utc)

# Function to calculate account age from creation date
def get_account_creation_date(snowflake):
    """Calculates account age in years, months, or days from Snowflake ID."""
    try:
        creation_date = snowflake_to_timestamp(snowflake)
        current_date = datetime.now(timezone.utc)  # Use UTC time
        delta = relativedelta(current_date, creation_date)

        if delta.years > 0:
            return f"{delta.years} year(s)"
        elif delta.months > 0:
            return f"{delta.months} month(s)"
        elif delta.days > 0:
            return f"{delta.days} day(s)"
        else:
            return "Less than a day old"
    except Exception as e:
        return f"Unknown (Error: {str(e)})"

# Function to get the formatted account creation date with month name
def get_formatted_creation_date(snowflake):
    """Returns the formatted account creation date with full month name."""
    creation_date = snowflake_to_timestamp(snowflake)
    return creation_date.strftime("%d %B %Y")  # Format as "12 December 2024"

# Function to generate headers for requests
def generate_headers(token):
    """Generate realistic headers for each request."""
    headers = {
        "Authorization": token,
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://discord.com/channels/@me",
        "Origin": "https://discord.com",
    }
    return headers

# Function to print detailed token information
def print_token_info(token, response):
    """Prints detailed information about a valid token."""
    user_data = response.json()
    username = f'{user_data["username"]}#{user_data["discriminator"]}'
    snowflake = user_data["id"]
    account_creation_date = get_account_creation_date(snowflake)
    formatted_creation_date = get_formatted_creation_date(snowflake)
    email = user_data.get("email", "Not linked")
    phone = user_data.get("phone", "Not linked")
    verified_email = user_data.get("verified", False)
    nitro = "Yes" if user_data.get("premium_type", 0) > 0 else "No"

    print(f"{Fore.GREEN}[VALID]{Style.RESET_ALL} Token: {token[:10]}...{token[-5:]}")
    print(f"  {Fore.CYAN}Username: {username}")
    print(f"  {Fore.CYAN}Account Creation Date: {formatted_creation_date}")
    print(f"  {Fore.CYAN}Account Age: {account_creation_date}")
    print(f"  {Fore.CYAN}Email: {email} ({'Verified' if verified_email else 'Not Verified'})")
    print(f"  {Fore.CYAN}Phone: {phone}")
    print(f"  {Fore.CYAN}Nitro Status: {nitro}\n")

# Function to check if a token is valid and retrieve account details
def check_token(token):
    """Check if a Discord token is valid and return its detailed information."""
    headers = generate_headers(token)
    try:
        response = requests.get(DISCORD_API, headers=headers, timeout=10)
        if response.status_code == 200:
            print_token_info(token, response)
            return True
        elif response.status_code == 401:
            print(f"{Fore.RED}[INVALID]{Style.RESET_ALL} Token: {token[:10]}...{token[-5:]}")
            return False
        else:
            print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} Unexpected status code {response.status_code} for token.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Request failed for token: {str(e)}")
        return False

# Function to process tokens with threading support
def process_tokens(tokens, max_threads):
    """Process the tokens and classify them as valid or invalid using threads."""
    valid_tokens = []
    invalid_tokens = []

    total_tokens = len(tokens)
    tokens_processed = 0

    # Use ThreadPoolExecutor for concurrent processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(check_token, token): token for token in tokens}
        
        # Wait for results and handle them
        for future in concurrent.futures.as_completed(futures):
            token = futures[future]
            is_valid = future.result()
            if is_valid:
                valid_tokens.append(token)
            else:
                invalid_tokens.append(token)

            tokens_processed += 1

            # Sleep to avoid rate limits
            time.sleep(3)

            # Random sleep (5-7 seconds) after every 10 tokens
            if tokens_processed % 10 == 0:
                print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Sleeping for a random time (5-7 seconds)...")
                time.sleep(random.randint(5, 7))

    # Write results to files
    with open(VALID_TOKENS_FILE, "w") as valid_file:
        valid_file.write("\n".join(valid_tokens))

    with open(INVALID_TOKENS_FILE, "w") as invalid_file:
        invalid_file.write("\n".join(invalid_tokens))

    print(f"\n{Fore.GREEN}Validation complete.{Style.RESET_ALL}")
    print(f"Valid tokens: {len(valid_tokens)}")
    print(f"Invalid tokens: {len(invalid_tokens)}")

# Main script entry point
if __name__ == "__main__":
    try:
        # Ask the user if they want to use threads and how many
        use_threads = input("Do you want to use threads? (yes/no): ").strip().lower()
        
        if use_threads == "yes":
            max_threads = int(input("How many threads would you like to use? (e.g., 10): ").strip())
        else:
            max_threads = 1  # No threads, single-threaded processing

        # Read tokens from file
        with open(TOKENS_FILE, "r") as file:
            tokens = [line.strip() for line in file if line.strip()]

        if not tokens:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} No tokens found in the file.")
        else:
            process_tokens(tokens, max_threads)
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {TOKENS_FILE} not found. Please create the file and add your tokens.")
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} An error occurred: {e}")
  
