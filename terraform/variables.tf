variable "project_id" {
  description = "The GCP project ID."
  type        = string
  default     = "project-2f3c2d48-8095-4bfd-991"
}

variable "region" {
  description = "The GCP region in which to create the Artifact Registry repository."
  type        = string
  default     = "us-central1"
}

variable "acceptable_hours" {
  description = "Comma-separated list of acceptable booking hours (24h). e.g. '18,19,20'"
  type        = string
  default     = "18,19,20"
}

variable "registry_id" {
  description = "The ID of the Artifact Registry Docker repository."
  type        = string
  default     = "tennis-court-registry"
}
