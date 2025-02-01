from pulumi import export, ResourceOptions
import pulumi_aws as aws
import json

# Define project name
project_name = "test"

# Create a new VPC
vpc = aws.ec2.Vpc(
    project_name + "-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
)

# Create public subnets in different availability zones
subnet1 = aws.ec2.Subnet(
    project_name + "-subnet-1",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    availability_zone="eu-central-1a",
)

subnet2 = aws.ec2.Subnet(
    project_name + "-subnet-2",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    map_public_ip_on_launch=True,
    availability_zone="eu-central-1b",
)

# Create private subnets in different Availability Zones for the database
subnet_db1 = aws.ec2.Subnet(
    project_name + "-db-subnet-1",
    vpc_id=vpc.id,
    cidr_block="10.0.5.0/24",
    map_public_ip_on_launch=False,
    availability_zone="eu-central-1a",
)

subnet_db2 = aws.ec2.Subnet(
    project_name + "-db-subnet-2",
    vpc_id=vpc.id,
    cidr_block="10.0.4.0/24",
    map_public_ip_on_launch=False,
    availability_zone="eu-central-1b",
)

# Create a DB Subnet Group covering both subnets
db_subnet_group = aws.rds.SubnetGroup(
    project_name + "-db-subnet-group",
    subnet_ids=[subnet_db1.id, subnet_db2.id],
    description="Subnet group for RDS",
)

# Create an Internet Gateway
igw = aws.ec2.InternetGateway(project_name + "-igw", vpc_id=vpc.id)

# Create a route table and associate it with the subnets
route_table = aws.ec2.RouteTable(project_name + "-route-table", vpc_id=vpc.id)
aws.ec2.Route(
    project_name + "-route",
    route_table_id=route_table.id,
    destination_cidr_block="0.0.0.0/0",
    gateway_id=igw.id,
)
aws.ec2.RouteTableAssociation(
    project_name + "-rta-1", route_table_id=route_table.id, subnet_id=subnet1.id
)
aws.ec2.RouteTableAssociation(
    project_name + "-rta-2", route_table_id=route_table.id, subnet_id=subnet2.id
)

# Create an ECS cluster
cluster = aws.ecs.Cluster(project_name + "-prod")

# Create a Security Groups
sg_web = aws.ec2.SecurityGroup(
    project_name + "-web-secgrp",
    vpc_id=vpc.id,
    description="Enable HTTP access",
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 80,
            "to_port": 80,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 3000,
            "to_port": 3000,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
    egress=[
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
)

sg_db = aws.ec2.SecurityGroup(
    project_name + "-db-secgrp",
    vpc_id=vpc.id,
    description="Allow access from backend only",
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 5432,
            "to_port": 5432,
            "security_groups": [sg_web.id],
        }
    ],
    egress=[
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
)

# Create a Load Balancer
alb = aws.lb.LoadBalancer(
    project_name + "-app-lb",
    security_groups=[sg_web.id],
    subnets=[subnet1.id, subnet2.id],
)

atg_frontend = aws.lb.TargetGroup(
    project_name + "-app-tg",
    port=80,
    protocol="HTTP",
    target_type="ip",
    vpc_id=vpc.id,
)

atg_backend = aws.lb.TargetGroup(
    project_name + "-backend-tg",
    port=3000,
    protocol="HTTP",
    target_type="ip",
    vpc_id=vpc.id,
    health_check={
        "path": "/api/health",
        "interval": 30,
        "timeout": 5,
        "healthy_threshold": 2,
        "unhealthy_threshold": 2,
    },
)

wl = aws.lb.Listener(
    project_name + "-web",
    load_balancer_arn=alb.arn,
    port=80,
    default_actions=[
        {"type": "forward", "target_group_arn": atg_frontend.arn}
    ],
)

wl_backend = aws.lb.ListenerRule(
    project_name + "-backend-rule",
    listener_arn=wl.arn,
    conditions=[
        {
            "pathPattern": {
                "values": ["/api/*"]
            }
        }
    ],
    actions=[{"type": "forward", "target_group_arn": atg_backend.arn}],
)

# Create an IAM Role
role = aws.iam.Role(
    project_name + "-task-exec-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2008-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
)

rpa = aws.iam.RolePolicyAttachment(
    project_name + "-task-exec-policy",
    role=role.name,
    policy_arn="arn:aws:iam::165111792849:policy/ecr_push",
)

# ECS Task Definitions
task_definition_frontend = aws.ecs.TaskDefinition(
    project_name + "-frontend-task",
    family="frontend-task-definition",
    cpu="256",
    memory="512",
    network_mode="awsvpc",
    requires_compatibilities=["FARGATE"],
    execution_role_arn=role.arn,
    container_definitions=json.dumps(
        [
            {
                "name": project_name + "-frontend",
                "image": "165111792849.dkr.ecr.eu-central-1.amazonaws.com/moba/app:main-a057c24",
                "portMappings": [{"containerPort": 80, "hostPort": 80, "protocol": "tcp"}],
            }
        ]
    ),
)

service_frontend = aws.ecs.Service(
    project_name + "-frontend-svc",
    cluster=cluster.arn,
    desired_count=2,
    launch_type="FARGATE",
    task_definition=task_definition_frontend.arn,
    network_configuration={
        "assign_public_ip": True,
        "subnets": [subnet1.id, subnet2.id],
        "security_groups": [sg_web.id],
    },
    load_balancers=[
        {
            "target_group_arn": atg_frontend.arn,
            "container_name": project_name + "-frontend",
            "container_port": 80,
        }
    ],
    opts=ResourceOptions(depends_on=[wl]),
)

task_definition_backend = aws.ecs.TaskDefinition(
    project_name + "-backend-task",
    family="backend-task-definition",
    cpu="256",
    memory="512",
    network_mode="awsvpc",
    requires_compatibilities=["FARGATE"],
    execution_role_arn=role.arn,
    container_definitions=json.dumps(
        [
            {
                "name": project_name + "-backend",
                "image": "165111792849.dkr.ecr.eu-central-1.amazonaws.com/moba/server:main-210c2f2",
                "portMappings": [{"containerPort": 3000, "protocol": "tcp"}]
            }
        ]
    ),
)

service_backend = aws.ecs.Service(
    project_name + "-backend-svc",
    cluster=cluster.arn,
    desired_count=2,
    launch_type="FARGATE",
    task_definition=task_definition_backend.arn,
    network_configuration={
        "assign_public_ip": True,
        "subnets": [subnet1.id, subnet2.id],
        "security_groups": [sg_web.id],
    },
    load_balancers=[
        {
            "target_group_arn": atg_backend.arn,
            "container_name": project_name + "-backend",
            "container_port": 3000,
        }
    ],
    opts=ResourceOptions(depends_on=[wl]),
)

# Create an RDS PostgreSQL database
db = aws.rds.Instance(
    project_name + "-db",
    engine="postgres",
    engine_version="16.3",
    instance_class="db.t3.micro",
    allocated_storage=20,
    db_name="database",
    username="admin",
    password="uh4QbgDqrNLY8PPs2ZW8",
    vpc_security_group_ids=[sg_db.id],
    db_subnet_group_name=db_subnet_group.name,
    publicly_accessible=False,
    skip_final_snapshot=True,
)

export("url", alb.dns_name)
export("db_endpoint", db.endpoint)
