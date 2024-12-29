# Discord Token Checker Tool

## Preview 
https://cdn.discordapp.com/attachments/1139500468427567185/1323008582177915030/Screenshot_2024-12-30-00-40-20-545_com.termux-edit.jpg?ex=6772f342&is=6771a1c2&hm=c3391cf17d5fd231464090f9f773fa80ddb98129e65708a3d38d5121e6ca7247&

This is a Python-based tool that checks the validity of Discord tokens. It verifies tokens by making requests to the Discord API and retrieves useful account information such as:

- Username
- Account creation date
- Account age (in years, months, or days)
- Email verification status
- Nitro status

## Features

- **Token Validation**: Checks if the Discord token is valid and retrieves account details.
- **Discord Snowflake ID**: Uses the Snowflake ID to calculate the account creation date and age.
- **Thread Support**: Optionally, the tool can run in multi-threaded mode to speed up token validation.
- **Rate Limiting**: Incorporates random sleep intervals to avoid Discord's rate limiting.
- **Detailed Account Information**: Displays account information including username, creation date, email, and Nitro status.

## Requirements

Before running the tool, ensure that you have Python 3.6+ installed along with the necessary dependencies:

- `requests`
- `colorama`
- `python-dateutil`

You can install these dependencies using pip:

``bash
pip install requests colorama python-dateutil``




# Donate

If you would like to support this project, you can donate via the following methods:

## Litecoin (LTC)
You can donate using Litecoin (LTC) to the following address:  
`ltc1qmy3jffpmvhl7wav64nhx0jweg6jyfsm5peq50z`

Thank you for your support!




