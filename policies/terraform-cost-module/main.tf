terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

locals {
  # Consolidated Standard 10-Tag FinOps Map
  mandatory_tags = {
    business_unit       = var.business_unit
    product             = var.product
    environment         = var.environment
    cost_centre         = var.cost_centre
    team                = var.team
    service             = var.service
    created_by          = var.created_by
    ttl                 = var.ttl
    compliance_scope    = var.compliance_scope
    data_classification = var.data_classification
    managed_by          = "terraform"
    finops_governed     = "true"
  }
}

# Example Cost-Governed EC2 Instance Launch Template
resource "aws_launch_template" "cost_governed_template" {
  name_prefix   = "lt-${var.service}-${var.environment}-"
  instance_type = var.instance_type

  tag_specifications {
    resource_type = "instance"
    tags          = local.mandatory_tags
  }

  tag_specifications {
    resource_type = "volume"
    tags          = local.mandatory_tags
  }

  tags = local.mandatory_tags
}
