data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_launch_template" "app" {
  name_prefix   = "${var.environment}-app-"
  image_id      = data.aws_ami.al2023.id
  instance_type = var.instance_type

  vpc_security_group_ids = [var.app_sg_id]

  iam_instance_profile {
    name = var.iam_instance_profile
  }

  monitoring {
    enabled = true # detailed CloudWatch monitoring, 1-min resolution
  }

  metadata_options {
    http_tokens   = "required" # IMDSv2 only
    http_endpoint = "enabled"
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -euxo pipefail
    dnf install -y docker
    systemctl enable --now docker
    docker run -d --name app --restart unless-stopped \
      -p ${var.app_port}:${var.app_port} \
      -e DATABASE_URL="$${DATABASE_URL}" \
      ${var.docker_image}
  EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags          = merge(var.tags, { Name = "${var.environment}-app-instance" })
  }
}

resource "aws_autoscaling_group" "app" {
  name                = "${var.environment}-app-asg"
  vpc_zone_identifier = var.private_subnet_ids
  target_group_arns   = [var.target_group_arn]

  min_size         = var.min_size
  max_size         = var.max_size
  desired_capacity = var.desired_capacity

  health_check_type         = "ELB"
  health_check_grace_period = 60

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  # Spread instances across AZs and terminate the oldest launch config first
  # during scale-in, favoring newer AMIs/templates staying in rotation.
  termination_policies = ["OldestLaunchTemplate", "OldestInstance"]

  dynamic "tag" {
    for_each = merge(var.tags, { Name = "${var.environment}-app-instance" })
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }
}

# Scale on CPU — target-tracking keeps things simple and self-correcting
resource "aws_autoscaling_policy" "cpu_target_tracking" {
  name                   = "${var.environment}-cpu-target-tracking"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 60
  }
}

# Scale on request count per target — catches I/O-bound load CPU alone would miss
resource "aws_autoscaling_policy" "request_count_target_tracking" {
  name                   = "${var.environment}-request-count-target-tracking"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${var.alb_arn_suffix}/${var.target_group_arn_suffix}"
    }
    target_value = 1000
  }
}
