output "tags" {
  value       = local.mandatory_tags
  description = "The consolidated 10-tag FinOps map applied to all resources."
}

output "launch_template_id" {
  value       = aws_launch_template.cost_governed_template.id
  description = "The ID of the cost-governed launch template."
}

output "launch_template_latest_version" {
  value       = aws_launch_template.cost_governed_template.latest_version
  description = "The latest version of the cost-governed launch template."
}
