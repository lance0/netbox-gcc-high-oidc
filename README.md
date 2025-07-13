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

---

## 1. Automated Configuration (Recommended)

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

---

## 2. Reverse Proxy Configuration

For SSO to work correctly, your reverse proxy must be configured to pass specific headers to the NetBox application. Below are example configurations for NGINX and Caddy.

### NGINX

This configuration is an expanded version of the one found in the official NetBox documentation. It includes best practices for security and performance.

Save this configuration to `/etc/nginx/sites-available/netbox` and create a symbolic link to `/etc/nginx/sites-enabled/`.

```nginx
# /etc/nginx/sites-available/netbox
server {
    listen 80;
    # Redirect all HTTP traffic to HTTPS
    server_name netbox.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name netbox.example.com;

    # SSL/TLS Configuration
    ssl_certificate /etc/ssl/certs/netbox.example.com.crt;
    ssl_certificate_key /etc/ssl/private/netbox.example.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;

    # HSTS (HTTP Strict Transport Security)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Proxy settings
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
    }

    # Static files
    location /static/ {
        alias /opt/netbox/netbox/project-static/;
    }
}
```

### Caddy

Caddy is a modern web server that automatically handles HTTPS. This configuration is simple and effective.

Save this configuration to your `Caddyfile` (e.g., `/etc/caddy/Caddyfile`).

```caddy
# /etc/caddy/Caddyfile
netbox.example.com {
    # Caddy automatically handles HTTPS certificates.

    # Reverse proxy requests to the NetBox application running on port 8001.
    reverse_proxy 127.0.0.1:8001 {
        # Caddy automatically sets the required X-Forwarded-* headers.
        # No extra configuration is needed for them.
    }

    # Serve static files directly from Caddy for better performance.
    handle_path /static/* {
        root * /opt/netbox/netbox/project-static
        file_server
    }

    # Log configuration
    log {
        output file /var/log/caddy/netbox.access.log
    }
}
```

---

## 3. Manual Configuration

If you prefer to edit the configuration file manually, follow these steps.

1.  **Open `configuration.py`:**
    The file is typically located at `/opt/netbox/netbox/netbox/configuration.py`.
    ```bash
    sudo -u netbox nano /opt/netbox/netbox/netbox/configuration.py
    ```

2.  **Add Configuration:**
    Add the following lines to the end of the file.

    ```python
    # OIDC settings for Azure GCC-High
    REMOTE_AUTH_BACKEND = 'social_core.backends.azuread.AzureADOAuth2'
    SOCIAL_AUTH_AZUREAD_OAUTH2_KEY = '{APPLICATION_ID}'
    SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET = '{SECRET_VALUE}'
    SOCIAL_AUTH_AZUREAD_OAUTH2_AUTHORITY_HOST = 'https://login.microsoftonline.us'

    # Enable remote authentication
    REMOTE_AUTH_ENABLED = True
    REMOTE_AUTH_AUTO_CREATE_USER = True
    ```

3.  **Save and Close** the file and **restart NetBox services**.

---

## Security Considerations

-   The Client Secret is a sensitive credential. This script uses `getpass` to ensure it is not exposed on your screen or in your command history.
-   After manual configuration, it is good practice to clear your command history (`history -c`) if the secret was pasted into the terminal.

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](./LICENSE) file for details.
