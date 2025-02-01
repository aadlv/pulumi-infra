import pulumi
import pulumi_aws as aws

# Define variables
project_name = "project_name"
aws_region = "eu-north-1"
instance_size = "t3.medium"

# Find the latest available Ubuntu AMI (any version)
amis = aws.ec2.get_ami(
    most_recent=True,
    owners=["099720109477"],  # Canonical's owner ID
    filters=[aws.ec2.GetAmiFilterArgs(
        name="name",
        values=["ubuntu/images/hvm-ssd/ubuntu-*-amd64-server-*"]
    )],
)
ami_id = amis.id

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
    availability_zone=f"{aws_region}a",
)

subnet2 = aws.ec2.Subnet(
    project_name + "-subnet-2",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    map_public_ip_on_launch=True,
    availability_zone=f"{aws_region}b",
)

# Create a Security Group
security_group = aws.ec2.SecurityGroup(
    project_name + "-web-sg",
    description="Allow HTTP, HTTPS, and 8080 traffic",
    vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(from_port=80, to_port=80, protocol="tcp", cidr_blocks=["0.0.0.0/0"]),
        aws.ec2.SecurityGroupIngressArgs(from_port=443, to_port=443, protocol="tcp", cidr_blocks=["0.0.0.0/0"]),
        aws.ec2.SecurityGroupIngressArgs(from_port=22, to_port=22, protocol="tcp", cidr_blocks=["0.0.0.0/0"]),
    ],
    egress=[aws.ec2.SecurityGroupEgressArgs(from_port=0, to_port=0, protocol="-1", cidr_blocks=["0.0.0.0/0"])],
)

# Create an Internet Gateway
igw = aws.ec2.InternetGateway(project_name + "-igw", vpc_id=vpc.id)

# Create a route table and associate it with the subnets
route_table = aws.ec2.RouteTable(
    project_name + "-route-table",
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        gateway_id=igw.id,
    )],
)

aws.ec2.RouteTableAssociation(
    project_name + "-rta-subnet-1",
    subnet_id=subnet1.id,
    route_table_id=route_table.id,
)

aws.ec2.RouteTableAssociation(
    project_name + "-rta-subnet-2",
    subnet_id=subnet2.id,
    route_table_id=route_table.id,
)

# Create an EC2 Instance
ec2_instance = aws.ec2.Instance(
    project_name + "-ec2",
    instance_type=instance_size,
    ami=ami_id,
    vpc_security_group_ids=[security_group.id],
    subnet_id=subnet1.id,  # Assign instance to the first subnet
    root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(volume_size=40),
    tags={"Name": project_name + "-ec2"},
)

# Create an Application Load Balancer
load_balancer = aws.lb.LoadBalancer(
    project_name + "-web-lb",
    internal=False,
    load_balancer_type="application",
    security_groups=[security_group.id],
    subnets=[subnet1.id, subnet2.id],
    tags={"Name": project_name + "-web-lb"},
)

# Create a Target Group
target_group = aws.lb.TargetGroup(
    project_name + "-web-tg",
    port=80,
    protocol="HTTP",
    vpc_id=vpc.id,
    health_check=aws.lb.TargetGroupHealthCheckArgs(
        path="/",
        protocol="HTTP",
    ),
    tags={"Name": project_name + "-web-tg"},
)

# Create a Listener
listener = aws.lb.Listener(
    project_name + "-web-lb-listener",
    load_balancer_arn=load_balancer.arn,
    port=80,
    protocol="HTTP",
    default_actions=[aws.lb.ListenerDefaultActionArgs(
        type="forward",
        target_group_arn=target_group.arn,
    )],
)

# Attach the EC2 Instance to the Target Group
target_group_attachment = aws.lb.TargetGroupAttachment(
    project_name + "-web-tg-attachment",
    target_group_arn=target_group.arn,
    target_id=ec2_instance.id,
    port=80,
)

# Export the Load Balancer's DNS name
pulumi.export("load_balancer_dns_name", load_balancer.dns_name)
