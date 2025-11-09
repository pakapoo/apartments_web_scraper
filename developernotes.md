### EC2 (Airflow)
* web server runs on port 8080, connect with <EC2 public IP>:8080
* username: admin, password: admin123
```bash
# Make sure the .pem file permission is set properly
chmod 400 <key.pem>

# Login
ssh -i "<.pem key>" ec2-user@<EC2 public IP>

# scp file from local to EC2
scp -i "<.pem key>" <local file path> ec2-user@<EC2 public IP>:<EC2 file path>
```

### Connect to RDS
* password: test1234
```bash
# Login, RDS endpoint example: apartments-rds.c5yi466cgccj.us-west-1.rds.amazonaws.com
mysql -h <RDS endpoint> -u admin -p
```

### How to create resources with AWS CLI
ECR (container image registry service)
```bash
# create repo, each repo stores 1 image, multiple versions are managed with 'tag'
aws ecr create-repository --repository-name apartments-web-scraper --region us-west-1
# The repo URL will look like:
# 493504727387.dkr.ecr.us-west-1.amazonaws.com/apartments-web-scraper

# get a temporary password from ECR for Docker login to ECR repo
aws ecr get-login-password --region us-west-1 | docker login --username AWS --password-stdin 493504727387.dkr.ecr.us-west-1.amazonaws.com
```

ECS (docker container, at least t2.small, or else Airflow UI will die easily)
```bash
# build image and push to ECR repo
# build amd64 else Mac will build with arm64 that doesn't work in ECS
# ECS Fargate only supports linux/amd64, so you must build for this platform even if you're on Apple Silicon
docker buildx build --platform linux/amd64 -t 493504727387.dkr.ecr.us-west-1.amazonaws.com/apartments-web-scraper:latest . --push

# register a ECS task with a predefined task definition file
# note that the 'executionRoleArn' is for ECS agent to create container, e.g. pull ECR image, connect to Cloudwatch, access SSM to store env variables, Secret Manager
# 'taskRoleArn' is for running the script (after container is created), for example you might interact with S3, RDS
# you AWS CLI account need to have ecs:RegisterTaskDefinition to perform this
aws ecs register-task-definition --cli-input-json file://apartments-web-scraper-def.json --region us-west-1

# create ECS cluster to run/manage tasks
aws ecs create-cluster --cluster-name apartment-scraper-cluster --region us-west-1

# run a task
aws ecs run-task \
  --cluster apartment-scraper-cluster \
  --task-definition apartments-flask:<ECS tag> \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-06d68a8171cf0f313,subnet-0cf148f75cd116d41],securityGroups=[sg-0443020b0c90476e5],assignPublicIp=ENABLED}" \
  --region us-west-1
```

Secret Manager (store sensitive data for Flask and Airflow to get data from RDS, other non-sensitive data are hardcoded directly in environment variables)
```bash
aws secretsmanager create-secret \
  --name apartments/db_credentials \
  --secret-string '{"<key1>":"<value1>","<key2>":"<value2>"}' \
  --region us-west-1
```

EC2 (for holding Airflow)
```bash
# install docker and docker compose
sudo yum update -y
sudo yum install -y docker git
sudo service docker start
sudo usermod -aG docker ec2-user
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose version

# run Airflow & Postgres with docker compose
docker-compose up -d
```

RDS (for serving Flask web app)
* created directly on UI
* remember to set 'Public access' to no, and set security group inbound rule
```bash
  Type: MySQL/Aurora
  Protocol: TCP
  Port Range: 3306
  Source: sg-xxxxxxxx (ECS task 的 security group)
```

Lambda (data cleaning and processing)
* create directly in UI
* 2 Layers: pandas_pyarrow_layer (by AWS) + sqlalchemy-layer (custom)