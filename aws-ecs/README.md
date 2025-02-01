# AWS Infrastructure with Pulumi

This project uses Pulumi to deploy a production-ready AWS ECS cluster with a PostgreSQL database and a load-balanced frontend and backend.

## Infrastructure Overview

### Resources
```sh
     Type                              Name                      Plan
 +   pulumi:pulumi:Stack               orbit-orbit               create
 +   ├─ aws:ecs:Cluster                example-prod              create
 +   ├─ aws:ec2:Vpc                    example-vpc               create
 +   ├─ aws:lb:TargetGroup             example-app-tg            create
 +   ├─ aws:ec2:RouteTable             example-route-table       create
 +   ├─ aws:ec2:Subnet                 example-subnet-2          create
 +   ├─ aws:ec2:Subnet                 example-db-subnet-2       create
 +   ├─ aws:ec2:Subnet                 example-db-subnet-1       create
 +   ├─ aws:ec2:SecurityGroup          example-web-secgrp        create
 +   ├─ aws:iam:Role                   example-task-exec-role    create
 +   ├─ aws:ec2:Subnet                 example-subnet-1          create
 +   ├─ aws:iam:RolePolicyAttachment   example-task-exec-policy  create
 +   ├─ aws:rds:SubnetGroup            example-db-subnet-group   create
 +   ├─ aws:ec2:RouteTableAssociation  example-rta-2             create
 +   ├─ aws:ec2:SecurityGroup          example-db-secgrp         create
 +   ├─ aws:lb:LoadBalancer            example-app-lb            create
 +   ├─ aws:lb:TargetGroup             example-backend-tg        create
 +   ├─ aws:ec2:RouteTableAssociation  example-rta-1             create
 +   ├─ aws:ec2:Route                  example-route             create
 +   ├─ aws:ecs:TaskDefinition         example-frontend-task     create
 +   ├─ aws:ec2:InternetGateway        example-igw               create
 +   ├─ aws:ecs:TaskDefinition         example-backend-task      create
 +   ├─ aws:lb:Listener                example-web               create
 +   ├─ aws:rds:Instance               example-db                create
 +   ├─ aws:lb:ListenerRule            example-backend-rule      create
 +   ├─ aws:ecs:Service                example-frontend-svc      create
 +   └─ aws:ecs:Service                example-backend-svc       create

 + 27 to create
```

### VPC & Networking
- A dedicated VPC with public and private subnets across two Availability Zones.
- An Internet Gateway and a route table for public subnets.
- A DB Subnet Group for RDS.

### Security Groups
- **Web Security Group**: Allows HTTP (80) and backend traffic (3000) from all sources.
- **Database Security Group**: Allows only backend access to PostgreSQL (5432).

### ECS & Load Balancing
- An ECS cluster with Fargate services for the frontend and backend.
- Application Load Balancer with separate target groups for frontend and backend.
- IAM Role for ECS Task Execution.

### Database
- PostgreSQL 16.3 instance on RDS with private subnet access.

## Prerequisites

1. Create build and push workflow in github actions which will build and push docker image to ECR
   - Example:
   ```sh
   - name: "[SERVER] Build, tag, and push image to Amazon ECR"
        if: steps.changes.outputs.server == 'true'
        id: build-backend-image
        working-directory: ./server
        env:
          REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          REPOSITORY: ${{ env.AWS_REPOSITORY_PREF }}/server
          IMAGE_TAG: ${{ steps.image_tag.outputs.image_tag }}
        run: |
          docker build -f Dockerfile -t $IMAGE_TAG .
          docker tag $IMAGE_TAG $REPOSITORY:$IMAGE_TAG
          docker push $REPOSITORY:$IMAGE_TAG
          echo "image_backend=$REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT
   ```
2. Install Pulumi CLI: [Installation Guide](https://www.pulumi.com/docs/install/)
3. Configure AWS credentials:
   ```sh
   aws configure
   ```
4. Ensure you have access to the required AWS resources (IAM, VPC, ECS, RDS, etc.).


## Outputs

- **ALB URL**: Public URL for accessing the frontend.
- **DB Endpoint**: Connection string for PostgreSQL.

## Notes
- The frontend and backend services pull images from ECR repositories.
