# saorsa-deploy

CLI tool for deploying testnets for [saorsa-node](https://github.com/jacderida/saorsa-node) using Terraform and Pyinfra.

## Prerequisites

- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) for package management
- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.0
- A Digital Ocean account with API token

## Installation

```bash
uv sync
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DO_TOKEN` | Digital Ocean API token (required) |
| `AWS_ACCESS_KEY_ID` | AWS credentials for Terraform state backend |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials for Terraform state backend |

Terraform state is stored in the `maidsafe-org-infra-tfstate` S3 bucket.

## Usage

### `infra` command

Provision VMs with attached storage volumes using Terraform.

```bash
uv run saorsa-deploy infra --name DEV-01 --node-count 10 --vm-count 3 --testnet
```

#### Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--attached-volume-size` | int | No | 20 | Size of attached volume in GB |
| `--name` | string | Yes | - | Deployment name (used as prefix in VM names) |
| `--node-count` | int | Yes | - | Number of nodes per VM |
| `--region-counts` | string | No | 3 | Comma-separated region counts per provider |
| `--testnet` | flag | No | - | Testnet mode: Digital Ocean only, lon1 region |
| `--vm-count` | int | Yes | - | Number of VMs per provider per region |

#### Examples

Deploy a testnet (single provider, single region):
```bash
uv run saorsa-deploy infra --name DEV-01 --node-count 10 --vm-count 3 --testnet
```

Deploy across 2 regions with larger volumes:
```bash
uv run saorsa-deploy infra --name PERF-05 --node-count 10 --vm-count 5 --region-counts 2 --attached-volume-size 50
```

### How it works

The `--name` argument is used as a prefix for all VM names (e.g., `DEV-01-saorsa-node-lon1-1`).

Before provisioning the main infrastructure, the tool creates a **bootstrap VM** (`{name}-saorsa-bootstrap`) via the Digital Ocean API. This single VM (s-2vcpu-4gb, Ubuntu 24.04, lon1) with a 35GB attached volume serves as the bootstrap node for the network.

The tool then uses Terraform to create Digital Ocean droplets (Ubuntu 24.04, s-2vcpu-4gb) with attached block storage volumes. Each VM gets one volume of the specified size, formatted as ext4.

For each provider/region combination, the tool:

1. Copies the Terraform manifests to an isolated workspace directory
2. Runs `terraform init` with a per-region state key
3. Runs `terraform apply` with the appropriate variables

All regions are provisioned in parallel (up to 5 concurrent Terraform runs). A live progress table shows the status of each region with elapsed time. On completion, a summary of total resources created is printed. If any region fails, the full Terraform error output is displayed.

### Supported Providers

Currently only Digital Ocean is supported. The architecture is designed for multiple providers -- adding a new provider involves creating a Terraform manifest directory and registering it in the provider config.

**Digital Ocean regions**: lon1, nyc1, ams3, sfo3, sgp1, blr1, fra1, tor1

## Development

### Running tests

```bash
uv run pytest tests/ -v
```

### Linting and formatting

```bash
uv run ruff format saorsa_deploy/ tests/
uv run ruff check saorsa_deploy/ tests/
```
