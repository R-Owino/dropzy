<!-- markdownlint-disable MD033 -->
<h1 align="center">Dropzy - Elegant Simplicity in File Sharing</h1>
<!-- markdownlint-enable MD033 -->

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/powered-by-black-magic.svg)](https://forthebadge.com)

[![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

[![CI](https://github.com/R-Owino/file-sharing/actions/workflows/cicd.yml/badge.svg)](https://github.com/R-Owino/file-sharing/actions/workflows/cicd.yml)
[![CI](https://github.com/R-Owino/file-sharing/actions/workflows/linting.yml/badge.svg)](https://github.com/R-Owino/file-sharing/actions/workflows/linting.yml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=shields)](http://makeapullrequest.com)

Dropzy is a simple web application that lets users share files from a common platform . Users can upload, download, view, search and delete files from the shared platform.

## Features

1. User authentication using Amazon Cognito.
2. File upload to Amazon S3.
3. File metadata upload to Amazon DynamoDB.
4. View a list of 15 most recent uploaded files with download and delete features.
5. Delete files from both Amazon S3 and Amazon DynamoDB.
6. File search functionality.
7. User account deletion.
8. User logout.

## The Architecture

The application follows this architecture:

![arch-diagram](some-link)

## Getting Started

- Clone the repository.

```bash
git clone https://github.com/R-Owino/file-sharing.git
```

- Navigate to the project directory.

```bash
cd file-sharing
```

- Create a virtual environment.

```bash
python -m venv venv
```

- Navigate to the infrastructure directory and create the infrastructure.

```bash
cd infra/
terraform apply -auto-approve
```

- Navigate to the scripts directory and run `generate-env.sh` script to populate your `/api/v1/.env` file.

```bash
./generate-env.sh
```

- Navigate to the api directory to set up Flask app.

```bash
cd api/
```

- Install the dependencies.

```bash
pip install -r requirements.txt
```

- Run the Redis docker container in detached mode. REDIS_PASSWORD is in your `/api/v1/.env` file.

```bash
docker run --name some-redis \
-d \
-p 6379:6379 \
-e REDIS PASSWORD=REDIS_PASSWORD \
redis redis-server \
--bind 127.0.0.1 \
--requirepass REDIS_PASSWORD
```

- Run your Flask app from the v1 directory.

```bash
cd v1/
flask run
```

- Enter `http://localhost:5000/` in a browser to see the application running.

### Run the Flask app using docker compose

If you have docker compose set up, follow these steps:

1. Navigate to the project root directory.
2. Build the docker compose then run it.

```bash
docker compose build
docker compose up
```

- Enter `http://0.0.0.0:5000/` in a browser to see the application running.

## Usage

To use Dropzy, follow these steps:

1. Open the project in your favorite code editor.
2. Modify the source code to fit your needs.
3. Build docker compose: **`docker compose build`**
4. Run the project: **`docker compose up`**
5. Use the project as desired.

## Contributing

If you'd like to contribute to Dropzy, here are some guidelines:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes.
4. Write tests to cover your changes.
5. Run the tests to ensure they pass.
6. Commit your changes.
7. Push your changes to your forked repository.
8. Submit a pull request.

## License

Dropzy is released under the MIT License. See the **[LICENSE](https://www.blackbox.ai/share/LICENSE)** file for details.

## Authors and Acknowledgment

Dropzy was created by **[Remmy](https://github.com/R-Owino)**.
