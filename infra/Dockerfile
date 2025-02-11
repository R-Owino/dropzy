FROM hashicorp/terraform:latest

WORKDIR /terraform
COPY infra/ /terraform/

RUN terraform init

CMD ["terraform" "apply", "--auto-approve"]
