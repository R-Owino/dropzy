FROM hashicorp/terraform:latest

RUN apk add --no-cache jq bash openssl

WORKDIR /terraform

COPY infra/main.tf infra/outputs.tf infra/providers.tf infra/variables.tf ./
COPY infra/modules/ ./modules/

RUN terraform init
