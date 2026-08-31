# Oracle Cloud Infrastructure - Monitoring Module
# Capstone Project: Enterprise DevOps Observability Platform

variable "compartment_id" {
  description = "Compartment OCID"
  type        = string
}

variable "project_name" {
  description = "Monitoring project name"
  type        = string
}

variable "alarm_email" {
  description = "Email for alarm notifications"
  type        = string
}

# Monitoring Compartment
resource "oci_logging_log_group" "platform" {
  compartment_id = var.compartment_id
  display_name   = "${var.project_name}-logs"
  description    = "Log group for DevOps platform"
}

# Platform Logs
resource "oci_logging_log" "oke_cluster" {
  display_name = "oke-cluster-logs"
  log_group_id = oci_logging_log_group.platform.id
  log_type     = "SERVICE"
  configuration {
    source {
      resource    = oci_containerengine_cluster.this.id
      category    = "all"
      service     = "oke"
      source_type = "OCISERVICE"
    }
  }
}

# Alarm - High CPU
resource "oci_monitoring_alarm" "high_cpu" {
  compartment_id = var.compartment_id
  display_name   = "High CPU Usage"
  severity       = "CRITICAL"
  query          = "CpuUtilization[5m]{resource_id = \"oke-cluster\"}.mean() > 90"
  metric_compartment_id = var.compartment_id
  destinations   = [var.alarm_email]
  is_enabled     = true
}

# Alarm - High Memory
resource "oci_monitoring_alarm" "high_memory" {
  compartment_id = var.compartment_id
  display_name   = "High Memory Usage"
  severity       = "WARNING"
  query          = "MemoryUtilization[5m]{resource_id = \"oke-cluster\"}.mean() > 85"
  metric_compartment_id = var.compartment_id
  destinations   = [var.alarm_email]
  is_enabled     = true
}

# Alarm - High Disk
resource "oci_monitoring_alarm" "high_disk" {
  compartment_id = var.compartment_id
  display_name   = "High Disk Usage"
  severity       = "WARNING"
  query          = "DiskUtilization[5m]{resource_id = \"oke-cluster\"}.mean() > 80"
  metric_compartment_id = var.compartment_id
  destinations   = [var.alarm_email]
  is_enabled     = true
}

# Alarm - Pod Restart
resource "oci_monitoring_alarm" "pod_restart" {
  compartment_id = var.compartment_id
  display_name   = "High Pod Restart Rate"
  severity       = "CRITICAL"
  query          = "PodRestarts[5m]{resource_id = \"oke-cluster\"}.sum() > 10"
  metric_compartment_id = var.compartment_id
  destinations   = [var.alarm_email]
  is_enabled     = true
}

output "log_group_id" {
  value = oci_logging_log_group.platform.id
}

output "alarm_ids" {
  value = [
    oci_monitoring_alarm.high_cpu.id,
    oci_monitoring_alarm.high_memory.id,
    oci_monitoring_alarm.high_disk.id,
    oci_monitoring_alarm.pod_restart.id,
  ]
}
