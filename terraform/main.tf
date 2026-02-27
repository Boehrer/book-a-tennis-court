resource "google_project_service" "artifactregistry" {
  project = var.project_id
  service = "artifactregistry.googleapis.com"

  disable_on_destroy = false
}

resource "google_project_service" "secretmanager" {
  project = var.project_id
  service = "secretmanager.googleapis.com"

  disable_on_destroy = false
}

resource "google_project_service" "cloudrun" {
  project = var.project_id
  service = "run.googleapis.com"

  disable_on_destroy = false
}

resource "google_project_service" "cloudscheduler" {
  project = var.project_id
  service = "cloudscheduler.googleapis.com"

  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "registry" {
  project       = var.project_id
  location      = var.region
  repository_id = var.registry_id
  format        = "DOCKER"
  description   = "Docker container registry for book-a-tennis-court"

  depends_on = [google_project_service.artifactregistry]
}

resource "google_service_account" "cloud_run_job" {
  project      = var.project_id
  account_id   = "tennis-court-job"
  display_name = "Tennis Court Cloud Run Job"
}

resource "google_service_account" "scheduler" {
  project      = var.project_id
  account_id   = "tennis-court-scheduler"
  display_name = "Tennis Court Cloud Scheduler"
}

resource "google_project_iam_member" "cloud_run_job_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run_job.email}"
}

resource "google_cloud_run_v2_job_iam_member" "scheduler_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_job.tennis_court.name
  role     = "roles/run.jobsExecutorWithOverrides"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
}


resource "google_cloud_run_v2_job" "tennis_court" {
  name                = "book-tennis-court"
  location            = var.region
  project             = var.project_id
  deletion_protection = false

  template {
    template {
      service_account = google_service_account.cloud_run_job.email
      max_retries     = 0

      containers {
        name  = "book-a-tennis-court"
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.registry_id}/book-a-tennis-court"

        resources {
          limits = {
            memory = "1Gi"
            cpu    = "1"
          }
        }

        env {
          name  = "ACCEPTABLE_HOURS"
          value = "19,20"
        }
        env {
          name = "EMAIL_ADDRESS"
          value_source {
            secret_key_ref {
              secret  = "email-address"
              version = "latest"
            }
          }
        }
        env {
          name = "PASSWORD"
          value_source {
            secret_key_ref {
              secret  = "password"
              version = "latest"
            }
          }
        }
        env {
          name = "CARD_HOLDER"
          value_source {
            secret_key_ref {
              secret  = "card-holder"
              version = "latest"
            }
          }
        }
        env {
          name = "CARD_NUMBER"
          value_source {
            secret_key_ref {
              secret  = "card-number"
              version = "latest"
            }
          }
        }
        env {
          name = "CVC"
          value_source {
            secret_key_ref {
              secret  = "cvc"
              version = "latest"
            }
          }
        }
        env {
          name = "EXPIRATION_MONTH"
          value_source {
            secret_key_ref {
              secret  = "expiration-month"
              version = "latest"
            }
          }
        }
        env {
          name = "EXPIRATION_YEAR"
          value_source {
            secret_key_ref {
              secret  = "expiration-year"
              version = "latest"
            }
          }
        }
        env {
          name = "EVENT_NAME"
          value_source {
            secret_key_ref {
              secret  = "event-name"
              version = "latest"
            }
          }
        }
        env {
          name = "URL"
          value_source {
            secret_key_ref {
              secret  = "url"
              version = "latest"
            }
          }
        }
      }
    }
  }

  depends_on = [google_project_service.cloudrun]
}

resource "google_cloud_scheduler_job" "tennis_court" {
  name      = "book-tennis-court-daily"
  project   = var.project_id
  region    = var.region
  schedule  = "57 6 * * 3,4,5"
  time_zone = "America/Chicago"

  http_target {
    http_method = "POST"
    uri         = "https://run.googleapis.com/v2/projects/${var.project_id}/locations/${var.region}/jobs/book-tennis-court:run"
    body        = base64encode(jsonencode({
      overrides = {
        containerOverrides = [{
          name = "book-a-tennis-court"
          env  = [{ name = "ACCEPTABLE_HOURS", value = "18,19,20,21" }]
        }]
      }
    }))

    headers = {
      "Content-Type" = "application/json"
    }

    oauth_token {
      service_account_email = google_service_account.scheduler.email
    }
  }

  depends_on = [google_project_service.cloudscheduler]
}

resource "google_cloud_scheduler_job" "tennis_court_weekend" {
  name      = "book-tennis-court-weekend"
  project   = var.project_id
  region    = var.region
  schedule  = "57 6 * * 0,1"
  time_zone = "America/Chicago"

  http_target {
    http_method = "POST"
    uri         = "https://run.googleapis.com/v2/projects/${var.project_id}/locations/${var.region}/jobs/book-tennis-court:run"
    body        = base64encode(jsonencode({
      overrides = {
        containerOverrides = [{
          name = "book-a-tennis-court"
          env  = [{ name = "ACCEPTABLE_HOURS", value = "13,14,15,16,17,18,19" }]
        }]
      }
    }))

    headers = {
      "Content-Type" = "application/json"
    }

    oauth_token {
      service_account_email = google_service_account.scheduler.email
    }
  }

  depends_on = [google_project_service.cloudscheduler]
}
