# EKS Base Infrastructure

## Overview
This repository contains a Pulumi script to provision AWS base infrastructure using AWS Fargate. The setup includes:

- A Virtual Private Cloud (VPC)
- Public and private subnets
- Internet Gateway and NAT Gateway
- Elastic Kubernetes Service (EKS) cluster
- IAM roles and policies for EKS and Fargate

## Resources

```sh
     Type                                          Name                                 Status              Info
 +   pulumi:pulumi:Stack                           test-eks-base-test-eks-base  created (763s)      
 +   ├─ aws:iam:Role                               test-eks-cluster-role            created (1s)
 +   ├─ aws:iam:Role                               test-fargate-pod-execution-role  created (1s)
 +   ├─ awsx:ec2:Vpc                               test-vpc                         created (3s)
 +   │  └─ aws:ec2:Vpc                             test-vpc                         created (3s)
 +   │     ├─ aws:ec2:Subnet                       test-vpc-private-1               created (1s)
 +   │     │  └─ aws:ec2:RouteTable                test-vpc-private-1               created (1s)
 +   │     │     ├─ aws:ec2:RouteTableAssociation  test-vpc-private-1               created (1s)
 +   │     │     └─ aws:ec2:Route                  test-vpc-private-1               created (1s)
 +   │     ├─ aws:ec2:Subnet                       test-vpc-private-2               created (2s)
 +   │     │  └─ aws:ec2:RouteTable                test-vpc-private-2               created (1s)
 +   │     │     ├─ aws:ec2:RouteTableAssociation  test-vpc-private-2               created (0.66s)
 +   │     │     └─ aws:ec2:Route                  test-vpc-private-2               created (1s)
 +   │     ├─ aws:ec2:InternetGateway              test-vpc                         created (1s)
 +   │     ├─ aws:ec2:Subnet                       test-vpc-public-2                created (11s)
 +   │     │  └─ aws:ec2:RouteTable                test-vpc-public-2                created (1s)
 +   │     │     ├─ aws:ec2:Route                  test-vpc-public-2                created (2s)
 +   │     │     └─ aws:ec2:RouteTableAssociation  test-vpc-public-2                created (2s)
 +   │     └─ aws:ec2:Subnet                       test-vpc-public-1                created (12s)
 +   │        ├─ aws:ec2:Eip                       test-vpc-1                       created (1s)
 +   │        ├─ aws:ec2:RouteTable                test-vpc-public-1                created (2s)
 +   │        │  ├─ aws:ec2:RouteTableAssociation  test-vpc-public-1                created (1s)
 +   │        │  └─ aws:ec2:Route                  test-vpc-public-1                created (2s)
 +   │        └─ aws:ec2:NatGateway                test-vpc-1                       created (95s)
 +   ├─ aws:iam:RolePolicyAttachment               test-eks-cluster-policy-2        created (0.63s)
 +   ├─ aws:iam:RolePolicyAttachment               test-eks-cluster-policy-1        created (1s)
 +   ├─ aws:iam:RolePolicyAttachment               test-fargate-ecr-policy          created (1s)
 +   ├─ aws:iam:RolePolicyAttachment               test-fargate-policy-1            created (2s)
 +   ├─ aws:eks:Cluster                            test-cluster                     created (465s)
 +   └─ aws:eks:FargateProfile                     test-fargate-profile             created (168s)
 + 30 created
```
## Infrastructure components

### 1. **VPC and Subnets**
- Creates a VPC (`10.0.0.0/16`)
- Public subnets (`10.0.1.0/24`, `10.0.2.0/24`)
- Private subnets (`10.0.3.0/24`, `10.0.4.0/24`)
- Associates subnets with appropriate route tables

### 2. **Networking Components**
- Internet Gateway for public subnets
- NAT Gateway for private subnets
- Route tables for public and private traffic handling

### 3. **IAM Roles and Policies**
- IAM role for EKS cluster with required policies
- IAM role for Fargate pod execution

### 4. **EKS Cluster & Fargate Profile**
- EKS cluster with public and private subnet access
- Fargate profile for running Rasa workloads

## Outputs

| Output Name          | Description                   |
|----------------------|-------------------------------|
| `vpc_id`            | ID of the created VPC         |
| `public_subnets`    | List of public subnet IDs     |
| `private_subnets`   | List of private subnet IDs    |
| `internet_gateway`  | ID of the Internet Gateway    |
| `eks_cluster_name`  | Name of the EKS cluster       |
| `eks_cluster_role`  | IAM Role for EKS cluster      |

## Notes

- The cluster **uses AWS Fargate**, eliminating the need for EC2 instances.
- No manual node group scaling is required.
- IAM roles are created for both the **EKS cluster** and the **Fargate profile**.
- Kubernetes workloads run on Fargate without requiring dedicated EC2 instances.
