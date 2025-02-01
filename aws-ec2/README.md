# AWS Infrastructure with Pulumi

This Pulumi script provisions an AWS infrastructure that includes:

- An EC2 instance running Ubuntu 24.04
- A security group allowing HTTP, HTTPS, and port 8080 traffic
- A Load Balancer to distribute traffic
- A Target Group for managing backend instance health checks
- Automatic attachment of the EC2 instance to the Target Group

## Prerequisites

Ensure you have the following installed:

- [Pulumi CLI](https://www.pulumi.com/docs/install/)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) (configured with credentials)
- [Python](https://www.python.org/downloads/) and `pip`
- Required Pulumi packages (`pulumi` and `pulumi-aws`)

## Resources Created
- EC2 Instance: Ubuntu 24.04 with t3.medium instance type.
- Security Group: Allows traffic on ports 80, 443, and 8080.
- Elastic Load Balancer (ELB): Routes HTTP traffic.
- Target Group: Monitors the health of backend instances.
- Instance Attachment: Automatically connects the EC2 instance to the Target Group.

```sh
     Type                              Name                  Plan
 +   pulumi:pulumi:Stack               example-dev           create
 +   ├─ aws:ec2:Vpc                    example-vpc           create
 +   ├─ aws:ec2:Subnet                 example-subnet-1      create
 +   ├─ aws:ec2:Subnet                 example-subnet-2      create
 +   ├─ aws:ec2:SecurityGroup          example-web-sg        create
 +   ├─ aws:ec2:InternetGateway        example-igw           create
 +   ├─ aws:lb:TargetGroup             example-web-tg        create
 +   ├─ aws:ec2:RouteTable             example-route-table   create
 +   ├─ aws:lb:Listener                web_lb_listener       create
 +   ├─ aws:ec2:RouteTableAssociation  example-rta-subnet-2  create
 +   ├─ aws:ec2:RouteTableAssociation  example-rta-subnet-1  create
 +   ├─ aws:lb:LoadBalancer            example-web-lb        create
 +   ├─ aws:lb:TargetGroupAttachment   web_tg_attachment     create
 +   └─ aws:ec2:Instance               example-ec2           create

+ 14 to create
```

## Outputs

- **ALB URL**: Public URL for accessing the app on port 80
