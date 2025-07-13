

import os

# --- Configuration ---
# The default location for the NetBox configuration file.
# If your configuration.py is in a different location, modify this variable.
NETBOX_CONFIG_PATH = "/opt/netbox/netbox/netbox/configuration.py"

# --- Helper Functions ---

def print_info(message):
    """Prints an informational message."""
    print(f"[INFO] {message}")

def print_success(message):
    """Prints a success message."""
    print(f"\033[92m[SUCCESS] {message}\033[0m")

def print_warning(message):
    """Prints a warning message."""
    print(f"\033[93m[WARNING] {message}\033[0m")

def print_error(message):
    """Prints an error message and exits."""
    print(f"\033[91m[ERROR] {message}\033[0m")
    exit(1)

def get_user_input(prompt_message):
    """Prompts the user for input and returns it."""
    value = input(prompt_message).strip()
    if not value:
        print_error("Input cannot be empty.")
    return value

def check_config_exists():
    """Checks if the configuration file exists."""
    if not os.path.exists(NETBOX_CONFIG_PATH):
        print_error(
            f"Configuration file not found at '{NETBOX_CONFIG_PATH}'.\n"
            "Please ensure the path is correct and you have run the initial NetBox setup."
        )
    print_info(f"Found configuration file at '{NETBOX_CONFIG_PATH}'.")

def read_config():
    """Reads the content of the configuration file."""
    try:
        with open(NETBOX_CONFIG_PATH, 'r') as f:
            return f.read()
    except IOError as e:
        print_error(f"Could not read the configuration file: {e}")

def write_config(content):
    """Writes content to the configuration file."""
    try:
        with open(NETBOX_CONFIG_PATH, 'a') as f:
            f.write(content)
    except IOError as e:
        print_error(f"Could not write to the configuration file: {e}")

# --- Main Logic ---

def main():
    """Main function to configure NetBox for GCC-High OIDC."""
    print_info("--- NetBox GCC-High OIDC Configuration Script ---")

    # 1. Check for the configuration file
    check_config_exists()
    config_content = read_config()

    # 2. Check if OIDC settings are already present
    if 'SOCIAL_AUTH_AZUREAD_OAUTH2_AUTHORITY_HOST' in config_content:
        print_warning("GCC-High OIDC settings already appear to be configured. Exiting.")
        return

    # 3. Get credentials from the user
    print_info("Please enter your Azure AD Application details.")
    app_id = get_user_input("Enter Application (Client) ID: ")
    secret_value = get_user_input("Enter Client Secret Value: ")

    # 4. Prepare the configuration block
    oidc_config = f"""
# --- GCC-High OIDC Configuration (added by script) ---
REMOTE_AUTH_BACKEND = 'social_core.backends.azuread.AzureADOAuth2'
SOCIAL_AUTH_AZUREAD_OAUTH2_KEY = '{app_id}'
SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET = '{secret_value}'
SOCIAL_AUTH_AZUREAD_OAUTH2_AUTHORITY_HOST = 'https://login.microsoftonline.us'

# Enable remote authentication and user creation
REMOTE_AUTH_ENABLED = True
REMOTE_AUTH_AUTO_CREATE_USER = True
# --- End of GCC-High OIDC Configuration ---
"""

    # 5. Append the configuration to the file
    print_info(f"Appending OIDC configuration to '{NETBOX_CONFIG_PATH}'...")
    write_config(oidc_config)

    print_success("Configuration successfully updated!")
    print_info(
        "Please restart the NetBox services for the changes to take effect:\n"
        "  sudo systemctl restart netbox netbox-rq"
    )

if __name__ == "__main__":
    main()

