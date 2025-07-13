# Configuring NetBox for Microsoft GCC-High OIDC Authentication

This document provides instructions for configuring NetBox to use Microsoft Office 365 Entra ID in a Government Community Cloud (GCC) High environment for Single Sign-On (SSO).

## Overview

NetBox utilizes the `python-social-auth` library to integrate with external authentication sources, including Azure AD (Entra ID). To connect to the GCC-High environment, the authentication endpoint (known as the authority host) must be changed from the default public endpoint to `https://login.microsoftonline.us`.

This can be accomplished by adding specific variables to your `configuration.py` file.

## Automated Configuration (Recommended)

A Python script is provided to automate this process. It will prompt you for the necessary credentials and append the required settings to your configuration file.

### Prerequisites

- You must have an active NetBox installation.
- You must have already created an **App Registration** in your Azure GCC-High tenant and have the following values:
    - **Application (Client) ID**
    - **Client Secret Value**

### Running the Script

1.  **Navigate to the scripts directory:**
    ```bash
    cd /opt/netbox/netbox/scripts/
    ```

2.  **Run the script as the NetBox user:**
    The script needs to be run with permissions to write to the `configuration.py` file.
    ```bash
    sudo -u netbox python3 configure_gcc_high_oidc.py
    ```

3.  **Follow the prompts:**
    The script will ask for your Application (Client) ID and Client Secret Value.

4.  **Restart NetBox Services:**
    After the script completes, you must restart the NetBox services for the changes to take effect.
    ```bash
    sudo systemctl restart netbox netbox-rq
    ```

## Manual Configuration

If you prefer to edit the configuration file manually, follow these steps.

1.  **Open `configuration.py`:**
    The file is typically located at `/opt/netbox/netbox/netbox/configuration.py`. Open it with your preferred text editor.
    ```bash
    sudo nano /opt/netbox/netbox/netbox/configuration.py
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

Your NetBox instance should now be configured to authenticate users against your GCC-High tenant.
