# NetBox GCC-High OIDC Configuration

A helper script to configure a [NetBox](https://github.com/netbox-community/netbox) instance to use Microsoft Office 365 Entra ID in a Government Community Cloud (GCC) High environment for Single Sign-On (SSO).

## Overview

NetBox utilizes the `python-social-auth` library to integrate with external authentication sources. To connect to a GCC-High environment, the authentication endpoint must be changed from the default public endpoint to `https://login.microsoftonline.us`.

This script automates the process by safely modifying your `configuration.py` file.

## Features

-   **Safe:** Automatically creates a timestamped backup of your configuration file before making changes.
-   **Secure:** Prompts for your Client Secret securely without displaying it on the screen or saving it in your shell history.
-   **Flexible:** Allows you to specify the path to your `configuration.py` file.
-   **User-Friendly:** Warns you if you are running as the root user to help prevent file permission issues.

## Prerequisites

Before you begin, you must have:

1.  A functioning NetBox installation.
2.  An **App Registration** created in your Azure GCC-High tenant.
3.  The **Application (Client) ID** from your App Registration.
4.  A **Client Secret Value** from your App Registration.

## Automated Configuration (Recommended)

The provided Python script will guide you through the configuration.

### Running the Script

1.  **Download the script**
    You can either clone this repository or download the `configure_gcc_high_oidc.py` script from the `scripts/` directory.

2.  **Make the script executable:**
    ```bash
    chmod +x scripts/configure_gcc_high_oidc.py
    ```

3.  **Run the script as the `netbox` user:**
    It is highly recommended to run the script as the user that owns the NetBox files to ensure correct file permissions. Provide the path to your `configuration.py` file as an argument.

    ```bash
    sudo -u netbox ./scripts/configure_gcc_high_oidc.py /opt/netbox/netbox/netbox/configuration.py
    ```
    If you do not provide a path, the script will default to `/opt/netbox/netbox/netbox/configuration.py`.

4.  **Follow the prompts:**
    The script will ask for your Application (Client) ID and your Client Secret Value.

5.  **Restart NetBox Services:**
    After the script completes, you must restart the NetBox services for the changes to take effect.
    ```bash
    sudo systemctl restart netbox netbox-rq
    ```

## Manual Configuration

If you prefer to edit the configuration file manually, follow these steps.

1.  **Open `configuration.py`:**
    The file is typically located at `/opt/netbox/netbox/netbox/configuration.py`. Open it with your preferred text editor.
    ```bash
    sudo -u netbox nano /opt/netbox/netbox/netbox/configuration.py
    ```

2.  **Add Configuration:**
    Add the following lines to the end of the file. Replace the placeholder values with your actual Azure AD credentials.

    ```python
    # OIDC settings for Azure GCC-High
    REMOTE_AUTH_BACKEND = 'social_core.backends.azuread.AzureADOAuth2'
    SOCIAL_AUTH_AZUREAD_OAUTH2_KEY = '{APPLICATION_ID}'  # Replace with your Azure AD Application (Client) ID
    SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET = '{SECRET_VALUE}' # Replace with your Azure AD Client Secret Value
    SOCIAL_AUTH_AZUREAD_OAUTH2_AUTHORITY_HOST = 'https://login.microsoftonline.us'

    # Enable remote authentication
    REMOTE_AUTH_ENABLED = True

    # Automatically create a local user account if one does not already exist
    REMOTE_AUTH_AUTO_CREATE_USER = True
    ```

3.  **Save and Close** the file.

4.  **Restart NetBox Services:**
    ```bash
    sudo systemctl restart netbox netbox-rq
    ```

## Security Considerations

-   The Client Secret is a sensitive credential. This script uses `getpass` to ensure it is not exposed on your screen or in your command history.
-   After manual configuration, it is good practice to clear your command history (`history -c`) if the secret was pasted into the terminal.

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](./LICENSE) file for details.