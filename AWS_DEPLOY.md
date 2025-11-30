# Deploying Sentinel Orchestrator Network to AWS Elastic Beanstalk

This guide explains how to deploy the full stack (Frontend, Backend, Masumi, Hydra) to AWS Elastic Beanstalk using Docker.

## Prerequisites

1.  **AWS CLI** installed and configured (`aws configure`).
2.  **EB CLI** installed (`pip install awsebcli`).
3.  **Docker** running locally.

## Step 1: Create ECR Repositories

Elastic Beanstalk cannot build images from source code on the fly easily. You must build them locally and push them to a container registry like Amazon ECR.

1.  Create repositories:
    ```bash
    aws ecr create-repository --repository-name son-backend
    aws ecr create-repository --repository-name son-frontend
    ```

2.  Login to ECR:
    ```bash
    aws ecr get-login-password --region <YOUR_REGION> | docker login --username AWS --password-stdin <YOUR_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com
    ```

## Step 2: Build and Push Images

1.  **Backend**:
    ```bash
    docker build -t son-backend ./backend
    docker tag son-backend:latest <YOUR_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com/son-backend:latest
    docker push <YOUR_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com/son-backend:latest
    ```

2.  **Frontend**:
    ```bash
    docker build -t son-frontend ./frontend
    docker tag son-frontend:latest <YOUR_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com/son-frontend:latest
    docker push <YOUR_ACCOUNT_ID>.dkr.ecr.<YOUR_REGION>.amazonaws.com/son-frontend:latest
    ```

## Step 3: Configure IAM Permissions (CRITICAL)

**This is the most common cause of deployment failure.**

The EC2 instances created by Elastic Beanstalk need permission to pull images from your ECR registry.

1.  Go to the **AWS IAM Console** -> **Roles**.
2.  Search for `aws-elasticbeanstalk-ec2-role`.
    *   *Note: If you created the environment with a custom instance profile, find that role instead.*
3.  Click on the role name.
4.  Click **Add permissions** -> **Attach policies**.
5.  Search for `AmazonEC2ContainerRegistryReadOnly`.
6.  Select it and click **Add permissions**.

Without this, you will get an error like: *"Instance deployment failed to download the Docker image."*

## Step 4: Configure Deployment File

1.  Open `docker-compose.prod.yml`.
2.  Replace `${AWS_ACCOUNT_ID}` and `${AWS_REGION}` with your actual values.
3.  Ensure environment variables (like `ADMIN_KEY`, `BLOCKFROST_API_KEY_PREPROD`) are set. You can set these in the Beanstalk console (Configuration -> Software) or replace them in the file.

## Step 4: Deploy to Elastic Beanstalk

1.  Initialize Beanstalk Application:
    ```bash
    eb init -p "Docker running on 64bit Amazon Linux 2023" son-network
    ```

2.  Create an Environment:
    ```bash
    eb create son-prod-env
    ```
    *   This will zip the current directory. Make sure `docker-compose.prod.yml` is renamed to `docker-compose.yml` for the deployment, OR configure EB to use the specific file.
    *   **Easier method**: Rename `docker-compose.prod.yml` to `docker-compose.yml` temporarily before deploying, or zip it manually:
        ```bash
        zip deploy.zip docker-compose.prod.yml
        # Upload deploy.zip to Beanstalk Console manually if CLI is tricky
        ```

3.  **Important**: In the Beanstalk Console, go to **Configuration** -> **Software** and set your Environment Properties:
    *   `ADMIN_KEY`
    *   `ENCRYPTION_KEY`
    *   `BLOCKFROST_API_KEY_PREPROD`

## Step 5: Access the Application

Once the environment is Green:
1.  Get the URL from `eb status` or the console.
2.  Your frontend will be available at that URL (mapped to port 80).
    *   *Note*: You may need to adjust the `docker-compose.prod.yml` ports to map `80:3000` for the frontend if you want it on the root URL.

## Troubleshooting

*   **502 Bad Gateway**: Check logs (`eb logs`). Usually means a container failed to start.
*   **Database Connection**: Ensure the `postgres` containers are healthy.
*   **CORS**: Update `NEXT_PUBLIC_API_URL` in the frontend environment variable to point to the Beanstalk URL, not localhost.
