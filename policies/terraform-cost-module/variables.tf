variable "business_unit" {
  type        = string
  description = "Mandatory Business Unit tag (retail-lending, msme-credit, risk-analytics, payments-core, platform-engineering)"
  validation {
    condition     = contains(["retail-lending", "msme-credit", "risk-analytics", "payments-core", "platform-engineering"], var.business_unit)
    error_message = "business_unit must be one of: retail-lending, msme-credit, risk-analytics, payments-core, platform-engineering."
  }
}

variable "product" {
  type        = string
  description = "Mandatory Product tag"
}

variable "environment" {
  type        = string
  description = "Mandatory Environment tag (prod, staging, dev, sandbox, dr)"
  validation {
    condition     = contains(["prod", "staging", "dev", "sandbox", "dr"], var.environment)
    error_message = "environment must be one of: prod, staging, dev, sandbox, dr."
  }
}

variable "cost_centre" {
  type        = string
  description = "Mandatory NetSuite Cost Centre code (CC-101 through CC-105)"
  validation {
    condition     = can(regex("^CC-10[1-5]$", var.cost_centre))
    error_message = "cost_centre must match pattern CC-101 to CC-105."
  }
}

variable "team" {
  type        = string
  description = "Mandatory Engineering squad ownership tag"
}

variable "service" {
  type        = string
  description = "Mandatory Microservice identifier"
}

variable "created_by" {
  type        = string
  description = "Mandatory SSO email or automated CI/CD pipeline identifier"
}

variable "ttl" {
  type        = string
  default     = "permanent"
  description = "Time-To-Live date (YYYY-MM-DD) for dev/sandbox or 'permanent' for prod"
}

variable "compliance_scope" {
  type        = string
  default     = "non-regulated"
  description = "Compliance boundary (pci-dss-cde, soc2-audit, rbi-core, gdpr-eu, non-regulated)"
}

variable "data_classification" {
  type        = string
  default     = "internal"
  description = "Data classification tier (restricted-pii, confidential-financial, internal, public)"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type (Validated against approved FinOps catalogue)"
  validation {
    condition = !can(regex(".*\\.(8xlarge|12xlarge|16xlarge|24xlarge|metal)$", var.instance_type))
    error_message = "Oversized instances (>4xlarge/metal) are blocked by FinOps policy. Submit an architectural exception."
  }
}
