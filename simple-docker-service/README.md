# Simple docker service

## Overview

Simple Docker Service is a lightweight, dockerized application designed to quickly spin up a web server for testing your infrastructure. It is perfect for scenarios where you need to verify the functionality of components like load balancers, networking, or basic service accessibility. For example, if you've provisioned infrastructure using Pulumi and want to check if your load balancer is functioning correctly, this service can be deployed to confirm everything is working smoothly.

## Prerequisites

To get started with the service, you will need:
- Docker

## Quick Start Guide

### Build the Docker Image

```sh
docker build -t aadlv-test .
```

### Start a web server on port 80

```sh
docker run -d --rm --name web-test -p 80:8000 aadlv-test:latest
```

### Test

```sh
$ curl -I localhost
HTTP/1.0 200 OK
```

### Stop web server

```sh
docker stop web-test
```
