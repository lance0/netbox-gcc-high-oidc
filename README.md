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

1.  A functioning NetBox installation (either bare metal or Docker).
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
    # For bare metal installs
    sudo -u netbox ./scripts/configure_gcc_high_oidc.py /opt/netbox/netbox/netbox/configuration.py

    # For Docker installs (run from your netbox-docker directory)
    sudo -u netbox ./scripts/configure_gcc_high_oidc.py configuration/configuration.py
    ```

4.  **Follow the prompts:**
    The script will ask for your Application (Client) ID and your Client Secret Value.

5.  **Restart NetBox Services:**
    After the script completes, you must restart the NetBox services for the changes to take effect.
    ```bash
    # For bare metal
    sudo systemctl restart netbox netbox-rq

    # For Docker
    docker compose restart
    ```

---

## 2. Reverse Proxy & Docker Considerations

For SSO to work correctly, your reverse proxy must be configured to pass specific headers to the NetBox application. The setup varies depending on whether you are running a bare metal installation or using Docker.

### Bare Metal Installation

If you installed NetBox directly on the host, your reverse proxy (NGINX, Caddy) will also run on the host and proxy traffic to NetBox on `localhost`.

<details>
<summary><b>NGINX Configuration (Bare Metal)</b></summary>

Save this configuration to `/etc/nginx/sites-available/netbox` and create a symbolic link to `/etc/nginx/sites-enabled/`.

```nginx
# /etc/nginx/sites-available/netbox
server {
    listen 80;
    server_name netbox.example.com;
    return 301 https://$host$request_uri; # Redirect HTTP to HTTPS
}

server {
    listen 443 ssl http2;
    server_name netbox.example.com;

    ssl_certificate /etc/ssl/certs/netbox.example.com.crt;
    ssl_certificate_key /etc/ssl/private/netbox.example.com.key;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/netbox/netbox/project-static/;
    }
}
```
</details>

<details>
<summary><b>Caddy Configuration (Bare Metal)</b></summary>

Save this configuration to your `Caddyfile` (e.g., `/etc/caddy/Caddyfile`).

```caddy
# /etc/caddy/Caddyfile
netbox.example.com {
    # Reverse proxy to NetBox on localhost
    reverse_proxy 127.0.0.1:8001

    # Serve static files
    handle_path /static/* {
        root * /opt/netbox/netbox/project-static
        file_server
    }
}
```
</details>

### Docker Installation

When using `netbox-docker`, the best practice is to run your reverse proxy as another container and connect it to the same Docker network.

**Key Concept:** From inside a container, `localhost` refers to the container itself. To reach the NetBox container, you must use its **service name** (e.g., `http://netbox:8080`).

Here is how to add Caddy as a reverse proxy to the standard `netbox-docker` setup.

1.  **Create a `docker-compose.override.yml` file** in your `netbox-docker` directory:

    ```yaml
    # netbox-docker/docker-compose.override.yml
    version: '3.4'
    services:
      caddy:
        image: caddy:2-alpine
        container_name: netbox-caddy
        restart: unless-stopped
        ports:
          - "80:80"
          - "443:443"
        volumes:
          - ./caddy/Caddyfile:/etc/caddy/Caddyfile:ro
          - ./caddy/data:/data
    ```

2.  **Create a `Caddyfile`** in a new `caddy` subdirectory:

    ```caddy
    # netbox-docker/caddy/Caddyfile
    netbox.example.com {
        # Reverse proxy to the NetBox container using its service name
        # The internal port for the NetBox container is 8080
        reverse_proxy netbox:8080

        # Serve static files from the NetBox container
        handle_path /static/* {
            reverse_proxy netbox:8080
        }
    }
    ```

3.  **Start the stack:**
    Run `docker compose up -d`. Caddy will now be running alongside NetBox and will automatically handle HTTPS for `netbox.example.com`.

---

## 3. Manual Configuration

If you prefer to edit the configuration file manually, follow these steps.

1.  **Open `configuration.py`:**
    ```bash
    # For bare metal
    sudo -u netbox nano /opt/netbox/netbox/netbox/configuration.py

    # For Docker
    nano configuration/configuration.py
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

3.  **Save and Close** the file and **restart NetBox**.

---

## Security Considerations

-   The Client Secret is a sensitive credential. This script uses `getpass` to ensure it is not exposed on your screen or in your command history.
-   After manual configuration, it is good practice to clear your command history (`history -c`) if the secret was pasted into the terminal.

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](./LICENSE) file for details.