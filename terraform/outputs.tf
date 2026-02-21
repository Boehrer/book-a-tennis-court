output "project_id" {
  description = "The ID of the GCP project."
  value       = var.project_id
}

output "registry_id" {
  description = "The Artifact Registry repository ID."
  value       = google_artifact_registry_repository.registry.repository_id
}

output "registry_hostname" {
  description = "The hostname to use when pushing/pulling Docker images (e.g. for 'docker tag' and 'docker push')."
  value       = "${var.region}-docker.pkg.dev"
}

output "registry_url" {
  description = "Full URL of the Artifact Registry repository."
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.registry.repository_id}"
}
