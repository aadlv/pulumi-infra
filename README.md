# Pulumi Infrastructure

## Overview

**Pulumi-Infra** is a collection of Pulumi python scripts for spinning up various infrastructure setups on AWS. This repository helps automate and manage cloud infrastructure using Pulumi's infrastructure-as-code approach.

## Features
- Modular Pulumi scripts for different infrastructure setups.
- Support for multiple cloud providers (for now AWS, in future: Azure, GCP, etc.).
- Easy deployment and teardown of resources.
- Reusable and configurable components for infrastructure management.

## Prerequisites

1. Install Pulumi CLI: [Installation Guide](https://www.pulumi.com/docs/install/)
2. Configure cloud provider credentials (e.g., AWS, Azure, GCP):
   ```sh
   pulumi config set cloud:provider <provider-name>
   ```
3. Ensure dependencies are installed:
   ```sh
   pip install pulumi pulumi-aws pulumi-azure pulumi-gcp
   ```

## Usage

### Create aws IAM and export AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
```sh
export AWS_ACCESS_KEY_ID=value
export AWS_SECRET_ACCESS_KEY=value
```

### Initializing a Pulumi Project on an empty folder, usually infra
```sh
pulumi new aws-python
```
### Before Deploying Infrastructure
- Replace __main__.py with __main__.py from this repo, choose which infra you want to provision
- Modify project_name variable inside __main__.py

### Deploying Infrastructure
```sh
pulumi up
```

### Viewing Stack Outputs
```sh
pulumi stack output
```

### Destroying Infrastructure
```sh
pulumi destroy
```

## Notes
- Each infrastructure module has its own `Pulumi.yaml` configuration file.
- Environment variables should not be used for sensitive credentials.
- Use different Pulumi stacks for managing multiple environments (dev, staging, production).

## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License.
