# Destroy Toan Bo Ha Tang Terraform Cua Alex

Tai lieu nay huong dan teardown toan bo ha tang AWS cua du an Alex sau khi da hoan thanh course project.

Muc tieu:

- destroy theo dung thu tu nguoc voi qua trinh hoc: Guide 8 ve Guide 2;
- tranh bo sot tai nguyen ton chi phi;
- tranh loi Terraform thuong gap nhu S3 bucket khong rong;
- giu rieng Guide 1 IAM permissions vi phan nay khong nam trong Terraform.

Source of truth:

1. code va Terraform hien tai trong repo;
2. README hien tai cua tung folder;
3. `guides/*.md`;
4. `scripts/destroy.py` chi dung cho Part 7, khong destroy toan bo project.

## Canh Bao Quan Trong

Destroy se xoa tai nguyen that tren AWS.

Nhung du lieu se mat vinh vien neu destroy:

- Aurora database trong Part 5: users, accounts, positions, jobs, reports, charts, retirement payloads;
- S3 Vectors / vector bucket trong Part 3: research knowledge base;
- frontend S3 static files;
- Lambda packages tren S3;
- CloudWatch dashboards Part 8.

Khong chay file nay nhu mot script. Hay doc tung buoc, chay tung command, kiem tra output, roi moi tiep tuc.

Khong in secrets:

- khong dump `.env`;
- khong dump `terraform.tfvars`;
- khong in API keys;
- khong dump Lambda environment variables day du.

## Thu Tu Destroy Chuan

Chay theo thu tu nguoc:

1. `terraform/8_enterprise`
2. `terraform/7_frontend`
3. `terraform/6_agents`
4. `terraform/5_database`
5. `terraform/4_researcher`
6. `terraform/3_ingestion`
7. `terraform/2_sagemaker`
8. Guide 1 IAM permissions: tu xoa thu cong neu muon

Ly do:

- Part 7 phu thuoc Part 5 va Part 6 local state;
- Part 6 phu thuoc database, SageMaker va S3 Vectors;
- Part 4 ghi vao ingest API Part 3;
- Part 3 phu thuoc SageMaker Part 2;
- Part 8 chi la monitoring/dashboard nen destroy dau tien an toan nhat.

## Pre-check Truoc Khi Destroy

Tu root project:

```bash
git status --short
```

Kiem tra AWS identity dang dung:

```bash
aws sts get-caller-identity
```

Kiem tra region mac dinh:

```bash
aws configure get region
```

Kiem tra cac Terraform state dang ton tai:

```bash
find terraform -maxdepth 2 -name terraform.tfstate -print
```

Trong repo hien tai, neu da deploy day du, ky vong co state o:

```text
terraform/2_sagemaker/terraform.tfstate
terraform/3_ingestion/terraform.tfstate
terraform/4_researcher/terraform.tfstate
terraform/5_database/terraform.tfstate
terraform/6_agents/terraform.tfstate
terraform/7_frontend/terraform.tfstate
terraform/8_enterprise/terraform.tfstate
```

Neu muon luu lai thong tin de audit truoc khi xoa, co the chay cac output khong sensitive:

```bash
cd terraform/8_enterprise && terraform output dashboard_names && cd ../..
cd terraform/7_frontend && terraform output cloudfront_url && terraform output api_gateway_url && cd ../..
cd terraform/6_agents && terraform output lambda_functions && terraform output sqs_queue_url && cd ../..
cd terraform/5_database && terraform output database_name && cd ../..
cd terraform/4_researcher && terraform output researcher_function_name && cd ../..
cd terraform/3_ingestion && terraform output vector_bucket_name && terraform output api_endpoint && cd ../..
cd terraform/2_sagemaker && terraform output sagemaker_endpoint_name && cd ../..
```

Khong chay `terraform output -raw api_key_value`.

## Buoc 1: Destroy Part 8 - Enterprise Dashboards

Tu guide/README hien tai, Part 8 tao CloudWatch dashboards:

- `alex-ai-model-usage`
- `alex-agent-performance`

Lenh:

```bash
cd terraform/8_enterprise
terraform init
terraform plan -destroy
terraform destroy
```

Khi Terraform hoi xac nhan, go:

```text
yes
```

Kiem tra sau destroy:

```bash
aws cloudwatch list-dashboards --dashboard-name-prefix alex
```

Quay ve root:

```bash
cd ../..
```

## Buoc 2: Destroy Part 7 - Frontend Va API

Part 7 gom:

- S3 bucket static frontend;
- CloudFront distribution;
- API Gateway HTTP API;
- Lambda `alex-api`;
- IAM role/policies cho API Lambda.

Guide 7 noi khi destroy everything thi chay reverse order `7, 6, 5, 4, 3, 2`.

Trong repo hien tai co `scripts/destroy.py`, nhung script do chi destroy Part 7. Tai lieu nay uu tien manual commands de ro tung buoc.

### 2.1 Lay ten frontend bucket

```bash
cd terraform/7_frontend
FRONTEND_BUCKET=$(terraform output -raw s3_bucket_name)
echo "${FRONTEND_BUCKET}"
```

### 2.2 Empty frontend bucket truoc khi Terraform destroy

S3 bucket phai rong truoc khi xoa:

```bash
aws s3 rm "s3://${FRONTEND_BUCKET}" --recursive
```

Neu bucket co versioning hoac delete markers, chay them:

```bash
aws s3api list-object-versions \
  --bucket "${FRONTEND_BUCKET}" \
  --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' \
  --output json > /tmp/alex-frontend-versions.json
```

Chi chay lenh delete versions neu file tren co objects:

```bash
aws s3api delete-objects \
  --bucket "${FRONTEND_BUCKET}" \
  --delete file:///tmp/alex-frontend-versions.json
```

Neu lenh bao `Invalid length for parameter Delete.Objects`, nghia la khong co versions de xoa; co the bo qua.

### 2.3 Destroy Terraform Part 7

```bash
terraform plan -destroy
terraform destroy
```

Khi Terraform hoi xac nhan, go:

```text
yes
```

CloudFront co the mat vai phut de disable/delete. Neu Terraform dang cho CloudFront, hay doi den khi command ket thuc.

Kiem tra sau destroy:

```bash
aws lambda get-function --function-name alex-api
aws apigatewayv2 get-apis --query "Items[?Name=='alex-api-gateway']"
aws s3 ls "s3://${FRONTEND_BUCKET}"
```

Mot so lenh verify co the tra loi `ResourceNotFoundException` hoac `NoSuchBucket`; do la ket qua mong muon sau destroy.

Quay ve root:

```bash
cd ../..
```

## Buoc 3: Destroy Part 6 - Agent Orchestra

Part 6 gom:

- SQS queue `alex-analysis-jobs`;
- SQS DLQ;
- S3 bucket `alex-lambda-packages-<account_id>`;
- 5 Lambda agents:
  - `alex-planner`
  - `alex-tagger`
  - `alex-reporter`
  - `alex-charter`
  - `alex-retirement`
- IAM role/policies;
- CloudWatch log groups.

Guide 7 noi destroy everything theo reverse order co Part 6 sau Part 7.

### 3.1 Empty Lambda package bucket

Terraform Part 6 tao bucket chua ZIP package. Neu bucket con object, `terraform destroy` co the fail.

```bash
cd terraform/6_agents
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
LAMBDA_PACKAGE_BUCKET="alex-lambda-packages-${ACCOUNT_ID}"
echo "${LAMBDA_PACKAGE_BUCKET}"
aws s3 rm "s3://${LAMBDA_PACKAGE_BUCKET}" --recursive
```

Neu bucket khong ton tai hoac da rong, co the tiep tuc.

### 3.2 Destroy Terraform Part 6

```bash
terraform init
terraform plan -destroy
terraform destroy
```

Khi Terraform hoi xac nhan, go:

```text
yes
```

Kiem tra sau destroy:

```bash
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'alex-')].FunctionName"
aws sqs list-queues --queue-name-prefix alex-analysis
aws s3 ls "s3://${LAMBDA_PACKAGE_BUCKET}"
```

Sau Part 6 destroy, cac job moi tu frontend se khong con duoc process.

Quay ve root:

```bash
cd ../..
```

## Buoc 4: Destroy Part 5 - Aurora Database

Part 5 gom:

- Aurora PostgreSQL Serverless v2 cluster;
- Aurora instance;
- DB subnet group;
- security group;
- Secrets Manager secret;
- IAM role/policy cho Data API access.

Guide 5 ghi:

```bash
cd terraform/5_database
terraform destroy
```

Canh bao: buoc nay xoa database va tat ca du lieu portfolio/job/report.

Lenh:

```bash
cd terraform/5_database
terraform init
terraform plan -destroy
terraform destroy
```

Khi Terraform hoi xac nhan, go:

```text
yes
```

Trong Terraform hien tai:

- `skip_final_snapshot = true`;
- secret co `recovery_window_in_days = 0`.

Nghia la destroy duoc toi uu cho moi truong hoc/dev, khong giu final snapshot.

Kiem tra sau destroy:

```bash
aws rds describe-db-clusters --db-cluster-identifier alex-aurora-cluster
aws secretsmanager list-secrets --query "SecretList[?contains(Name, 'alex-aurora-credentials')].Name"
```

`DBClusterNotFoundFault` la ket qua mong muon neu cluster da bi xoa.

Quay ve root:

```bash
cd ../..
```

## Buoc 5: Destroy Part 4 - Researcher

Part 4 implementation hien tai khac guide cu:

- khong con App Runner;
- Researcher chay bang Lambda container image;
- co ECR repository `alex-researcher`;
- co Lambda Function URL;
- co optional EventBridge scheduler 12 gio.

Guide 4 ghi:

```bash
# Navigate to the terraform/4_researcher directory
terraform destroy
```

Lenh:

```bash
cd terraform/4_researcher
terraform init
terraform plan -destroy
terraform destroy
```

Khi Terraform hoi xac nhan, go:

```text
yes
```

ECR repository trong Terraform co `force_delete = true`, nen image trong repo se duoc xoa cung repository.

Kiem tra sau destroy:

```bash
aws lambda get-function --function-name alex-researcher
aws ecr describe-repositories --repository-names alex-researcher
aws scheduler list-schedules --name-prefix alex-research
```

`ResourceNotFoundException` hoac `RepositoryNotFoundException` la ket qua mong muon sau destroy.

Quay ve root:

```bash
cd ../..
```

## Buoc 6: Destroy Part 3 - Ingestion Pipeline Va S3 Vectors

Part 3 gom:

- bucket `alex-vectors-<account_id>`;
- S3 Vectors permissions/index access;
- Lambda `alex-ingest`;
- API Gateway REST API `/ingest`;
- API key va usage plan;
- CloudWatch log group.

Guide 3 ghi:

```bash
# From the terraform directory
terraform destroy
```

Guide 3 cung canh bao rang destroy Part 3 se pha ha tang ingest. Trong repo hien tai, Part 3 khong destroy SageMaker Part 2 vi SageMaker nam trong folder doc lap `terraform/2_sagemaker`.

### 6.1 Optional: cleanup S3 Vectors data qua script

Neu muon xoa vectors bang application script truoc:

```bash
cd backend/ingest
uv run cleanup_s3vectors.py
cd ../..
```

Script nay yeu cau xac nhan va se xoa vectors trong index.

### 6.2 Empty vector bucket truoc khi Terraform destroy

```bash
cd terraform/3_ingestion
VECTOR_BUCKET=$(terraform output -raw vector_bucket_name)
echo "${VECTOR_BUCKET}"
aws s3 rm "s3://${VECTOR_BUCKET}" --recursive
```

Bucket Part 3 co versioning enabled, nen can xu ly versions/delete markers neu co.

List versions:

```bash
aws s3api list-object-versions \
  --bucket "${VECTOR_BUCKET}" \
  --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' \
  --output json > /tmp/alex-vector-versions.json
```

Delete versions neu file co objects:

```bash
aws s3api delete-objects \
  --bucket "${VECTOR_BUCKET}" \
  --delete file:///tmp/alex-vector-versions.json
```

List delete markers:

```bash
aws s3api list-object-versions \
  --bucket "${VECTOR_BUCKET}" \
  --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' \
  --output json > /tmp/alex-vector-delete-markers.json
```

Delete markers neu file co objects:

```bash
aws s3api delete-objects \
  --bucket "${VECTOR_BUCKET}" \
  --delete file:///tmp/alex-vector-delete-markers.json
```

Neu lenh delete bao `Invalid length for parameter Delete.Objects`, nghia la khong co object trong nhom do; co the bo qua.

### 6.3 Destroy Terraform Part 3

```bash
terraform init
terraform plan -destroy
terraform destroy
```

Khi Terraform hoi xac nhan, go:

```text
yes
```

Kiem tra sau destroy:

```bash
aws lambda get-function --function-name alex-ingest
aws apigateway get-rest-apis --query "items[?name=='alex-api']"
aws s3 ls "s3://${VECTOR_BUCKET}"
```

Quay ve root:

```bash
cd ../..
```

## Buoc 7: Destroy Part 2 - SageMaker Embedding Endpoint

Part 2 gom:

- SageMaker endpoint `alex-embedding-endpoint`;
- endpoint configuration;
- SageMaker model;
- IAM role `alex-sagemaker-role`;
- policy attachment.

Guide 2 ghi:

```bash
cd terraform/2_sagemaker
terraform destroy
```

Lenh:

```bash
cd terraform/2_sagemaker
terraform init
terraform plan -destroy
terraform destroy
```

Khi Terraform hoi xac nhan, go:

```text
yes
```

Kiem tra sau destroy:

```bash
aws sagemaker describe-endpoint --endpoint-name alex-embedding-endpoint
aws sagemaker describe-model --model-name alex-embedding-model
aws iam get-role --role-name alex-sagemaker-role
```

`ValidationException` cho SageMaker endpoint/model hoac `NoSuchEntity` cho IAM role la ket qua mong muon sau destroy.

Quay ve root:

```bash
cd ../..
```

## Guide 1 - IAM Permissions

Guide 1 khong co Terraform folder.

No co the da tao:

- IAM group `AlexAccess`;
- custom policy `AlexS3VectorsAccess`;
- attach AWS managed policies vao group;
- add IAM user `aiengineer` vao group.

Theo yeu cau hien tai, IAM user/group/policy se duoc ban tu huy thu cong neu muon.

Tai lieu nay khong huong dan xoa IAM chi tiet de tranh vo tinh anh huong cac lab/course khac.

## Verification Tong Hop Sau Khi Destroy

Chay cac lenh nay tu root hoac bat ky folder nao.

### Lambda

```bash
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'alex-')].FunctionName"
```

Ky vong: danh sach rong hoac khong con function `alex-*` cua project.

### SQS

```bash
aws sqs list-queues --queue-name-prefix alex
```

Ky vong: khong con queue `alex-analysis-jobs` hoac DLQ.

### RDS / Aurora

```bash
aws rds describe-db-clusters --query "DBClusters[?contains(DBClusterIdentifier, 'alex')].DBClusterIdentifier"
```

Ky vong: rong.

### SageMaker

```bash
aws sagemaker list-endpoints --name-contains alex
```

Ky vong: khong con `alex-embedding-endpoint`.

### S3 Buckets

```bash
aws s3 ls | rg "alex-"
```

Ky vong: khong con bucket `alex-frontend-*`, `alex-lambda-packages-*`, `alex-vectors-*`.

### ECR

```bash
aws ecr describe-repositories --query "repositories[?contains(repositoryName, 'alex')].repositoryName"
```

Ky vong: khong con `alex-researcher`.

### API Gateway REST va HTTP API

```bash
aws apigateway get-rest-apis --query "items[?contains(name, 'alex')].name"
aws apigatewayv2 get-apis --query "Items[?contains(Name, 'alex')].Name"
```

Ky vong: rong.

### CloudWatch Dashboards

```bash
aws cloudwatch list-dashboards --dashboard-name-prefix alex
```

Ky vong: rong.

### CloudWatch Log Groups

Terraform co the xoa log groups do no quan ly, nhung neu co log group con sot thi co the la do resource duoc tao ngoai Terraform.

Kiem tra:

```bash
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/alex
```

Neu muon xoa log group con sot, xoa thu cong sau khi chac chan khong can logs nua.

## Troubleshooting

### Loi: S3 bucket is not empty

Nguyen nhan:

- bucket con object;
- bucket co versioning, con object versions;
- bucket co delete markers.

Cach xu ly:

```bash
aws s3 rm "s3://<bucket-name>" --recursive
```

Neu bucket co versioning:

```bash
aws s3api list-object-versions \
  --bucket "<bucket-name>" \
  --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' \
  --output json > /tmp/versions.json

aws s3api delete-objects \
  --bucket "<bucket-name>" \
  --delete file:///tmp/versions.json
```

Lap lai voi `DeleteMarkers` neu can.

### Loi: CloudFront distribution deletion takes long

CloudFront can disable distribution truoc khi delete. Terraform co the cho vai phut.

Khong kill command neu no van dang polling binh thuong.

### Loi: Terraform state missing

Neu `terraform.tfstate` mat nhung resource con tren AWS, Terraform khong biet resource nao de destroy.

Huong xu ly:

1. Kiem tra resource con sot bang AWS Console/AWS CLI;
2. Neu can, import resource vao state roi destroy;
3. Hoac xoa thu cong tren AWS Console neu resource don gian va ban chac chan.

Khong xoa file state truoc khi destroy.

### Loi: Resource already deleted

Neu resource da bi xoa thu cong truoc do, `terraform destroy` co the bao not found.

Thu:

```bash
terraform refresh
terraform destroy
```

Neu van loi, can xu ly state bang `terraform state rm <address>` cho resource da mat. Chi lam khi da chac resource khong con tren AWS.

### Loi: Terraform provider crash

Guide 6 da ghi nhan provider crash co the la transient.

Thu chay lai:

```bash
terraform destroy
```

### Loi: Dependency destroy sai thu tu

Neu destroy Part 5 database truoc Part 7/6, API/agents co the con reference ARN da mat.

Thu tu dung:

```text
8 -> 7 -> 6 -> 5 -> 4 -> 3 -> 2
```

## Cost Checklist Cuoi Cung

Sau khi destroy xong, vao AWS Billing / Cost Explorer de kiem tra cac service co the con chi phi:

- RDS / Aurora;
- SageMaker;
- Lambda;
- API Gateway;
- CloudFront;
- S3;
- SQS;
- ECR;
- CloudWatch Logs;
- EventBridge Scheduler;
- Secrets Manager.

Nen kiem tra lai sau 24 gio vi mot so metric billing co do tre.

## Tom Tat Lenh Destroy Chinh

Day la ban rut gon. Chi chay sau khi da doc cac canh bao va buoc empty bucket o tren.

```bash
cd terraform/8_enterprise && terraform destroy && cd ../..
cd terraform/7_frontend && terraform destroy && cd ../..
cd terraform/6_agents && terraform destroy && cd ../..
cd terraform/5_database && terraform destroy && cd ../..
cd terraform/4_researcher && terraform destroy && cd ../..
cd terraform/3_ingestion && terraform destroy && cd ../..
cd terraform/2_sagemaker && terraform destroy && cd ../..
```

Neu bat ky buoc nao fail, dung lai, doc phan Troubleshooting, sua dung buoc do, roi moi tiep tuc buoc tiep theo.
