# book-a-tennis-court

Automatically books a tennis court at the Chicago Park District using Selenium.

## How it works

A Cloud Run job runs the Selenium script on a schedule (Sundays at 7am Central). It books a court 6 days in advance at the hours configured in `ACCEPTABLE_HOURS`.

## Setup

### 1. Configure secrets

Secrets are stored in Google Secret Manager and must be added manually. Create each secret in your GCP project:

| Secret ID          | Description                        |
|--------------------|------------------------------------|
| `url`              | Booking page URL                   |
| `email-address`    | Login email                        |
| `password`         | Login password                     |
| `card-holder`      | Name on card                       |
| `card-number`      | Credit card number                 |
| `cvc`              | Card CVC                           |
| `expiration-month` | Card expiration month              |
| `expiration-year`  | Card expiration year               |
| `event-name`       | Name for the booking event         |

You can use `secrets.sh` as a template — fill in your values and run it to populate Secret Manager:

```sh
./secrets.sh
```

> **Note:** `secrets.sh` and `.env` are gitignored and should never be committed.

### 2. Configure push.sh

Update the `REGISTRY` variable in `push.sh` to match your Artifact Registry URL:

```sh
REGISTRY="<region>-docker.pkg.dev/<project-id>/<registry-id>"
```

### 3. Deploy infrastructure

```sh
cd terraform
terraform init
terraform apply
```

### 4. Build and push the Docker image

```sh
./push.sh
```

## Running locally

Create a `.env` file with your secrets (see `.env` for the expected format), then:

```sh
# Run with Python directly
export $(cat .env | xargs) && python3 main.py

# Run with Docker
docker build -t book-a-tennis-court . && docker run --platform linux/amd64 --shm-size=2g --env-file .env book-a-tennis-court
```

## Configuration

| Variable           | Description                                      | Default      |
|--------------------|--------------------------------------------------|--------------|
| `ACCEPTABLE_HOURS` | Comma-separated 24h hours to attempt booking     | `18,19,20`   |

The scheduler overrides `ACCEPTABLE_HOURS` at invocation time — update it in `terraform/main.tf` under `google_cloud_scheduler_job.tennis_court`.
