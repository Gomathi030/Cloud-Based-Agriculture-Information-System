# Cloud-Based-Agriculture-Information-System
 1. Project Overview

The Cloud-Based Agriculture Information System is a web-based application designed to help farmers access useful agricultural information through a centralized platform.

The system provides farmer registration and login, crop information, weather forecasts, and market price information. It uses AWS cloud services to host the frontend, process backend requests, and store application data securely.

2. Problem Statement

Farmers face several challenges in accessing important agricultural information required for effective farming and decision-making. Crop details, weather information, and agricultural market prices are often available through different sources, making it difficult and time-consuming for farmers to collect the required information in one place.

Major Problems

Lack of Centralized Information: Farmers need to depend on multiple sources to obtain agricultural information.

Difficulty in Accessing Crop Details: Finding useful information about different crops and their cultivation can be challenging.

Weather Information Challenges: Farmers need timely weather information to plan their agricultural activities.

Lack of Market Price Awareness: Farmers may find it difficult to access updated agricultural market prices.

Time-Consuming Information Collection: Collecting information from different platforms requires additional time and effort.

Limited Accessibility: Farmers need a simple and user-friendly platform to access agricultural information.

3. Proposed System

Our Cloud-Based Agriculture Information System addresses these challenges using AWS cloud infrastructure, including Application Load Balancing, Auto Scaling, private networking, Amazon RDS managed database services, Amazon S3 for frontend hosting, Amazon CloudFront for content delivery, and Amazon CloudWatch for infrastructure monitoring.

4. Architecture Diagram

Cloud-Based Agriculture Information System follows a three-tier AWS architecture consisting of the Presentation Layer, Application Layer, and Database Layer.

![AWS Architecture Diagram](./images/agri%20architecture.jpeg)

1. Presentation Layer – Frontend

AWS Services:

Amazon S3

Amazon CloudFront

Technologies:

HTML

CSS

JavaScript

Responsibilities:

Amazon S3 stores the static frontend files.

Amazon CloudFront delivers frontend content securely using HTTPS.

Farmers access the application through the CloudFront URL.

No custom domain name is required.

2. Application Layer – Backend

AWS Services:

Amazon VPC

Application Load Balancer (ALB)

Amazon EC2

Auto Scaling Group

Bastion Host

Technologies:

Python

Flask

Responsibilities:

The Application Load Balancer distributes incoming API requests.

Backend EC2 instances run the Flask application inside private subnets.

Auto Scaling automatically adjusts the number of EC2 instances based on application demand.

The Bastion Host provides secure SSH access to private EC2 instances.

The backend handles application logic such as registration, login, and crop-related operations.

3. Database Layer – Data Storage

AWS Service:

Amazon RDS (MySQL)

Responsibilities:

Stores farmer information.

Stores crop-related information.

Stores market-related data.

Database access is restricted to the backend application in the private subnet.

 AWS Services Used

AWS Service

Purpose

Amazon CloudFront

Secure frontend content delivery

Amazon S3

Static frontend hosting

Application Load Balancer

Distributes API requests

Amazon EC2

Runs the Flask backend

Auto Scaling Group

Automatically scales backend EC2 instances

Amazon RDS (MySQL)

Managed relational database

Bastion Host

Secure SSH access to private resources

Amazon CloudWatch

Monitors application health and logs

Amazon VPC

Provides isolated cloud networking