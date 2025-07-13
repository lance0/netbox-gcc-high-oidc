#!/usr/bin/env python3
import os
import sys
import argparse
import getpass
import shutil
from datetime import datetime

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
    sys.exit(1)

def get_user_input(prompt_message):
    """Prompts the user for non-sensitive input and returns it."""
    value = input(prompt_message).strip()
    if not value:
        print_error("Input cannot be empty.")
    return value

def get_secret_input(prompt_message):
    """Prompts the user for sensitive input using getpass."""
    value = getpass.getpass(prompt_message).strip()
    if not value:
        print_error("Secret cannot be empty.")
    return value

def backup_config(config_path):
    """Creates a timestamped backup of the configuration file."""
    backup_path = f"{config_path}.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
    try:
        shutil.copy2(config_path, backup_path)
        print_info(f"Created backup of configuration at '{backup_path}'.")
    except IOError as e:
        print_error(f"Could not create backup file: {e}")

def check_root_user():
    """Checks if the script is being run as the root user."""
    if os.geteuid() == 0:
        print_warning(
            "Running as the root user is not recommended.\n"
            "This can cause issues with file permissions.\n"
            "It is recommended to run this script as the 'netbox' user, e.g.:\n"
            "  sudo -u netbox ./configure_gcc_high_oidc.py /opt/netbox/netbox/configuration.py"
        )
        if input("Continue anyway? (y/n): ").lower() != 'y':
            print_info("Exiting.")
            sys.exit(0)

# --- Main Logic ---

def main(args):
    """Main function to configure NetBox for GCC-High OIDC."""
    print_info("--- NetBox GCC-High OIDC Configuration Script ---")
    check_root_user()

    config_path = args.config_file

    # 1. Check for the configuration file
    if not os.path.exists(config_path):
        print_error(
            f"Configuration file not found at '{config_path}'.\n"
            "Please ensure the path is correct and you have run the initial NetBox setup."
        )
    print_info(f"Found configuration file at '{config_path}'.")

    # 2. Read the configuration
    try:
        with open(config_path, 'r') as f:
            config_content = f.read()
    except IOError as e:
        print_error(f"Could not read the configuration file: {e}")

    # 3. Check if OIDC settings are already present
    if 'SOCIAL_AUTH_AZUREAD_OAUTH2_AUTHORITY_HOST' in config_content:
        print_warning("GCC-High OIDC settings already appear to be configured. Exiting.")
        return

    # 4. Create a backup
    backup_config(config_path)

    # 5. Get credentials from the user
    print_info("Please enter your Azure AD Application details.")
    app_id = get_user_input("Enter Application (Client) ID: ")
    secret_value = get_secret_input("Enter Client Secret Value: ")

    # 6. Prepare the configuration block
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

    # 7. Append the configuration to the file
    try:
        with open(config_path, 'a') as f:
            f.write(oidc_config)
    except IOError as e:
        print_error(f"Could not write to the configuration file: {e}")

    print_success("Configuration successfully updated!")
    print_info(
        "Please restart the NetBox services for the changes to take effect:\n"
        "  sudo systemctl restart netbox netbox-rq"
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Configure NetBox for Microsoft GCC-High OIDC authentication."
    )
    parser.add_argument(
        "config_file",
        help="The full path to your NetBox configuration.py file.",
        default="/opt/netbox/netbox/netbox/configuration.py",
        nargs='?'
    )
    args = parser.parse_args()
    main(args)