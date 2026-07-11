# Destroy Toàn Bộ Hạ Tầng Terraform Của Alex

Tài liệu này hướng dẫn teardown toàn bộ hạ tầng AWS của dự án Alex sau khi đã hoàn thành course project.

Mục tiêu:

- destroy theo đúng thứ tự ngược với quá trình học: Guide 8 về Guide 2;
- tránh bỏ sót tài nguyên còn phát sinh chi phí;
- tránh lỗi Terraform thường gặp như S3 bucket không rỗng;
- tách riêng Guide 1 IAM permissions vì phần này không nằm trong Terraform.

Source of truth:

1. code và Terraform hiện tại trong repo;
2. README hiện tại của từng folder;
3. `guides/*.md`;
4. `scripts/destroy.py` chỉ dùng cho Part 7, không destroy toàn bộ project.

## Cảnh Báo Quan Trọng

Destroy sẽ xóa tài nguyên thật trên AWS.

Những dữ liệu sẽ mất vĩnh viễn nếu destroy:

- Aurora database trong Part 5: users, accounts, positions, jobs, reports, charts, retirement payloads;
- S3 Vectors / vector bucket trong Part 3: research knowledge base;
- frontend S3 static files;
- Lambda packages trên S3;
- CloudWatch dashboards Part 8.

Không chạy tài liệu này như một script. Hãy đọc từng bước, chạy từng command, kiểm tra output, rồi mới tiếp tục.

Không in secrets:

- không dump `.env`;
- không dump `terraform.tfvars`;
- không in API keys;
- không dump đầy đủ Lambda environment variables.

## Thứ Tự Destroy Chuẩn

Chạy theo thứ tự ngược:

1. `terraform/8_enterprise`
2. `terraform/7_frontend`
3. `terraform/6_agents`
4. `terraform/5_database`
5. `terraform/4_researcher`
6. `terraform/3_ingestion`
7. `terraform/2_sagemaker`
8. Guide 1 IAM permissions: tự xóa thủ công nếu muốn

Lý do:

- Part 7 phụ thuộc Part 5 và Part 6 local state;
- Part 6 phụ thuộc database, SageMaker và S3 Vectors;
- Part 4 ghi vào ingest API Part 3;
- Part 3 phụ thuộc SageMaker Part 2;
- Part 8 chỉ là monitoring/dashboard nên destroy đầu tiên là an toàn nhất.

## Pre-check Trước Khi Destroy

Từ root project:

```bash
git status --short
```

Kiểm tra AWS identity đang dùng:

```bash
aws sts get-caller-identity
```

Kiểm tra region mặc định:

```bash
aws configure get region
```

Kiểm tra các Terraform state đang tồn tại:

```bash
find terraform -maxdepth 2 -name terraform.tfstate -print
```

Trong repo hiện tại, nếu đã deploy đầy đủ, kỳ vọng có state ở:

```text
terraform/2_sagemaker/terraform.tfstate
terraform/3_ingestion/terraform.tfstate
terraform/4_researcher/terraform.tfstate
terraform/5_database/terraform.tfstate
terraform/6_agents/terraform.tfstate
terraform/7_frontend/terraform.tfstate
terraform/8_enterprise/terraform.tfstate
```

Nếu muốn lưu lại thông tin audit trước khi xóa, có thể chạy các output không sensitive:

```bash
cd terraform/8_enterprise && terraform output dashboard_names && cd ../..
cd terraform/7_frontend && terraform output cloudfront_url && terraform output api_gateway_url && cd ../..
cd terraform/6_agents && terraform output lambda_functions && terraform output sqs_queue_url && cd ../..
cd terraform/5_database && terraform output database_name && cd ../..
cd terraform/4_researcher && terraform output researcher_function_name && cd ../..
cd terraform/3_ingestion && terraform output vector_bucket_name && terraform output api_endpoint && cd ../..
cd terraform/2_sagemaker && terraform output sagemaker_endpoint_name && cd ../..
```

Không chạy:

```bash
terraform output -raw api_key_value
```

## Bước 1: Destroy Part 8 - Enterprise Dashboards

Part 8 tạo CloudWatch dashboards:

- `alex-ai-model-usage`
- `alex-agent-performance`

Lệnh:

```bash
cd terraform/8_enterprise
terraform init
terraform plan -destroy
terraform destroy
```

Khi Terraform hỏi xác nhận, gõ:

```text
yes
```

Kiểm tra sau destroy:

```bash
aws cloudwatch list-dashboards --dashboard-name-prefix alex
```

Quay về root:

```bash
cd ../..
```

## Bước 2: Destroy Part 7 - Frontend Và API

Part 7 gồm:

- S3 bucket static frontend;
- CloudFront distribution;
- API Gateway HTTP API;
- Lambda `alex-api`;
- IAM role/policies cho API Lambda.

Guide 7 ghi rằng khi destroy everything thì chạy reverse order `7, 6, 5, 4, 3, 2`.

Trong repo hiện tại có `scripts/destroy.py`, nhưng script đó chỉ destroy Part 7. Tài liệu này ưu tiên manual commands để rõ từng bước.

### 2.1 Lấy tên frontend bucket

```bash
cd terraform/7_frontend
FRONTEND_BUCKET=$(terraform output -raw s3_bucket_name)
echo "${FRONTEND_BUCKET}"
```

### 2.2 Empty frontend bucket trước khi Terraform destroy

S3 bucket phải rỗng trước khi xóa:

```bash
aws s3 rm "s3://${FRONTEND_BUCKET}" --recursive
```

Nếu bucket có versioning hoặc delete markers, chạy thêm:

```bash
aws s3api list-object-versions \
  --bucket "${FRONTEND_BUCKET}" \
  --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' \
  --output json > /tmp/alex-frontend-versions.json
```

Chỉ chạy lệnh delete versions nếu file trên có objects:

```bash
aws s3api delete-objects \
  --bucket "${FRONTEND_BUCKET}" \
  --delete file:///tmp/alex-frontend-versions.json
```

Nếu lệnh báo `Invalid length for parameter Delete.Objects`, nghĩa là không có versions để xóa; có thể bỏ qua.

### 2.3 Destroy Terraform Part 7

```bash
terraform plan -destroy
terraform destroy
```

Khi Terraform hỏi xác nhận, gõ:

```text
yes
```

CloudFront có thể mất vài phút để disable/delete. Nếu Terraform đang chờ CloudFront, hãy đợi đến khi command kết thúc.

Kiểm tra sau destroy:

```bash
aws lambda get-function --function-name alex-api
aws apigatewayv2 get-apis --query "Items[?Name=='alex-api-gateway']"
aws s3 ls "s3://${FRONTEND_BUCKET}"
```

Một số lệnh verify có thể trả lời `ResourceNotFoundException` hoặc `NoSuchBucket`; đó là kết quả mong muốn sau destroy.

Quay về root:

```bash
cd ../..
```

## Bước 3: Destroy Part 6 - Agent Orchestra

Part 6 gồm:

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

Guide 7 ghi destroy everything theo reverse order, trong đó Part 6 chạy sau Part 7.

### 3.1 Empty Lambda package bucket

Terraform Part 6 tạo bucket chứa ZIP package. Nếu bucket còn object, `terraform destroy` có thể fail.

```bash
cd terraform/6_agents
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
LAMBDA_PACKAGE_BUCKET="alex-lambda-packages-${ACCOUNT_ID}"
echo "${LAMBDA_PACKAGE_BUCKET}"
aws s3 rm "s3://${LAMBDA_PACKAGE_BUCKET}" --recursive
```

Nếu bucket không tồn tại hoặc đã rỗng, có thể tiếp tục.

### 3.2 Destroy Terraform Part 6

```bash
terraform init
terraform plan -destroy
terraform destroy
```

Khi Terraform hỏi xác nhận, gõ:

```text
yes
```

Kiểm tra sau destroy:

```bash
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'alex-')].FunctionName"
aws sqs list-queues --queue-name-prefix alex-analysis
aws s3 ls "s3://${LAMBDA_PACKAGE_BUCKET}"
```

Sau Part 6 destroy, các job mới từ frontend sẽ không còn được process.

Quay về root:

```bash
cd ../..
```

## Bước 4: Destroy Part 5 - Aurora Database

Part 5 gồm:

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

Cảnh báo: bước này xóa database và toàn bộ dữ liệu portfolio/job/report.

Lệnh:

```bash
cd terraform/5_database
terraform init
terraform plan -destroy
terraform destroy
```

Khi Terraform hỏi xác nhận, gõ:

```text
yes
```

Trong Terraform hiện tại:

- `skip_final_snapshot = true`;
- secret có `recovery_window_in_days = 0`.

Nghĩa là destroy được tối ưu cho môi trường học/dev, không giữ final snapshot.

Kiểm tra sau destroy:

```bash
aws rds describe-db-clusters --db-cluster-identifier alex-aurora-cluster
aws secretsmanager list-secrets --query "SecretList[?contains(Name, 'alex-aurora-credentials')].Name"
```

`DBClusterNotFoundFault` là kết quả mong muốn nếu cluster đã bị xóa.

Quay về root:

```bash
cd ../..
```

## Bước 5: Destroy Part 4 - Researcher

Part 4 implementation hiện tại khác guide cũ:

- không còn App Runner;
- Researcher chạy bằng Lambda container image;
- có ECR repository `alex-researcher`;
- có Lambda Function URL;
- có optional EventBridge scheduler 12 giờ.

Guide 4 ghi:

```bash
# Navigate to the terraform/4_researcher directory
terraform destroy
```

Lệnh:

```bash
cd terraform/4_researcher
terraform init
terraform plan -destroy
terraform destroy
```

Khi Terraform hỏi xác nhận, gõ:

```text
yes
```

ECR repository trong Terraform có `force_delete = true`, nên image trong repo sẽ được xóa cùng repository.

Kiểm tra sau destroy:

```bash
aws lambda get-function --function-name alex-researcher
aws ecr describe-repositories --repository-names alex-researcher
aws scheduler list-schedules --name-prefix alex-research
```

`ResourceNotFoundException` hoặc `RepositoryNotFoundException` là kết quả mong muốn sau destroy.

Quay về root:

```bash
cd ../..
```

## Bước 6: Destroy Part 3 - Ingestion Pipeline Và S3 Vectors

Part 3 gồm:

- bucket `alex-vectors-<account_id>`;
- S3 Vectors permissions/index access;
- Lambda `alex-ingest`;
- API Gateway REST API `/ingest`;
- API key và usage plan;
- CloudWatch log group.

Guide 3 ghi:

```bash
# From the terraform directory
terraform destroy
```

Guide 3 cũng cảnh báo rằng destroy Part 3 sẽ phá hạ tầng ingest. Trong repo hiện tại, Part 3 không destroy SageMaker Part 2 vì SageMaker nằm trong folder độc lập `terraform/2_sagemaker`.

### 6.1 Optional: cleanup S3 Vectors data qua script

Nếu muốn xóa vectors bằng application script trước:

```bash
cd backend/ingest
uv run cleanup_s3vectors.py
cd ../..
```

Script này yêu cầu xác nhận và sẽ xóa vectors trong index.

### 6.2 Empty vector bucket trước khi Terraform destroy

```bash
cd terraform/3_ingestion
VECTOR_BUCKET=$(terraform output -raw vector_bucket_name)
echo "${VECTOR_BUCKET}"
aws s3 rm "s3://${VECTOR_BUCKET}" --recursive
```

Bucket Part 3 có versioning enabled, nên cần xử lý versions/delete markers nếu có.

List versions:

```bash
aws s3api list-object-versions \
  --bucket "${VECTOR_BUCKET}" \
  --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' \
  --output json > /tmp/alex-vector-versions.json
```

Delete versions nếu file có objects:

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

Delete markers nếu file có objects:

```bash
aws s3api delete-objects \
  --bucket "${VECTOR_BUCKET}" \
  --delete file:///tmp/alex-vector-delete-markers.json
```

Nếu lệnh delete báo `Invalid length for parameter Delete.Objects`, nghĩa là không có object trong nhóm đó; có thể bỏ qua.

### 6.3 Destroy Terraform Part 3

```bash
terraform init
terraform plan -destroy
terraform destroy
```

Khi Terraform hỏi xác nhận, gõ:

```text
yes
```

Kiểm tra sau destroy:

```bash
aws lambda get-function --function-name alex-ingest
aws apigateway get-rest-apis --query "items[?name=='alex-api']"
aws s3 ls "s3://${VECTOR_BUCKET}"
```

Quay về root:

```bash
cd ../..
```

## Bước 7: Destroy Part 2 - SageMaker Embedding Endpoint

Part 2 gồm:

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

Lệnh:

```bash
cd terraform/2_sagemaker
terraform init
terraform plan -destroy
terraform destroy
```

Khi Terraform hỏi xác nhận, gõ:

```text
yes
```

Kiểm tra sau destroy:

```bash
aws sagemaker describe-endpoint --endpoint-name alex-embedding-endpoint
aws sagemaker describe-model --model-name alex-embedding-model
aws iam get-role --role-name alex-sagemaker-role
```

`ValidationException` cho SageMaker endpoint/model hoặc `NoSuchEntity` cho IAM role là kết quả mong muốn sau destroy.

Quay về root:

```bash
cd ../..
```

## Guide 1 - IAM Permissions

Guide 1 không có Terraform folder.

Nó có thể đã tạo:

- IAM group `AlexAccess`;
- custom policy `AlexS3VectorsAccess`;
- attach AWS managed policies vào group;
- add IAM user `aiengineer` vào group.

Theo yêu cầu hiện tại, IAM user/group/policy sẽ được bạn tự hủy thủ công nếu muốn.

Tài liệu này không hướng dẫn xóa IAM chi tiết để tránh vô tình ảnh hưởng các lab/course khác.

## Verification Tổng Hợp Sau Khi Destroy

Chạy các lệnh này từ root hoặc bất kỳ folder nào.

### Lambda

```bash
aws lambda list-functions --query "Functions[?starts_with(FunctionName, 'alex-')].FunctionName"
```

Kỳ vọng: danh sách rỗng hoặc không còn function `alex-*` của project.

### SQS

```bash
aws sqs list-queues --queue-name-prefix alex
```

Kỳ vọng: không còn queue `alex-analysis-jobs` hoặc DLQ.

### RDS / Aurora

```bash
aws rds describe-db-clusters --query "DBClusters[?contains(DBClusterIdentifier, 'alex')].DBClusterIdentifier"
```

Kỳ vọng: rỗng.

### SageMaker

```bash
aws sagemaker list-endpoints --name-contains alex
```

Kỳ vọng: không còn `alex-embedding-endpoint`.

### S3 Buckets

```bash
aws s3 ls | rg "alex-"
```

Kỳ vọng: không còn bucket `alex-frontend-*`, `alex-lambda-packages-*`, `alex-vectors-*`.

### ECR

```bash
aws ecr describe-repositories --query "repositories[?contains(repositoryName, 'alex')].repositoryName"
```

Kỳ vọng: không còn `alex-researcher`.

### API Gateway REST và HTTP API

```bash
aws apigateway get-rest-apis --query "items[?contains(name, 'alex')].name"
aws apigatewayv2 get-apis --query "Items[?contains(Name, 'alex')].Name"
```

Kỳ vọng: rỗng.

### CloudWatch Dashboards

```bash
aws cloudwatch list-dashboards --dashboard-name-prefix alex
```

Kỳ vọng: rỗng.

### CloudWatch Log Groups

Terraform có thể xóa log groups do nó quản lý, nhưng nếu có log group còn sót thì có thể là do resource được tạo ngoài Terraform.

Kiểm tra:

```bash
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/alex
```

Nếu muốn xóa log group còn sót, xóa thủ công sau khi chắc chắn không cần logs nữa.

## Troubleshooting

### Lỗi: S3 bucket is not empty

Nguyên nhân:

- bucket còn object;
- bucket có versioning, còn object versions;
- bucket có delete markers.

Cách xử lý:

```bash
aws s3 rm "s3://<bucket-name>" --recursive
```

Nếu bucket có versioning:

```bash
aws s3api list-object-versions \
  --bucket "<bucket-name>" \
  --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' \
  --output json > /tmp/versions.json

aws s3api delete-objects \
  --bucket "<bucket-name>" \
  --delete file:///tmp/versions.json
```

Lặp lại với `DeleteMarkers` nếu cần.

### Lỗi: CloudFront distribution deletion takes long

CloudFront cần disable distribution trước khi delete. Terraform có thể chờ vài phút.

Không kill command nếu nó vẫn đang polling bình thường.

### Lỗi: Terraform state missing

Nếu `terraform.tfstate` mất nhưng resource còn trên AWS, Terraform không biết resource nào để destroy.

Hướng xử lý:

1. Kiểm tra resource còn sót bằng AWS Console/AWS CLI;
2. Nếu cần, import resource vào state rồi destroy;
3. Hoặc xóa thủ công trên AWS Console nếu resource đơn giản và bạn chắc chắn.

Không xóa file state trước khi destroy.

### Lỗi: Resource already deleted

Nếu resource đã bị xóa thủ công trước đó, `terraform destroy` có thể báo not found.

Thử:

```bash
terraform refresh
terraform destroy
```

Nếu vẫn lỗi, cần xử lý state bằng `terraform state rm <address>` cho resource đã mất. Chỉ làm khi đã chắc resource không còn trên AWS.

### Lỗi: Terraform provider crash

Guide 6 đã ghi nhận provider crash có thể là transient.

Thử chạy lại:

```bash
terraform destroy
```

### Lỗi: Dependency destroy sai thứ tự

Nếu destroy Part 5 database trước Part 7/6, API/agents có thể còn reference ARN đã mất.

Thứ tự đúng:

```text
8 -> 7 -> 6 -> 5 -> 4 -> 3 -> 2
```

## Cost Checklist Cuối Cùng

Sau khi destroy xong, vào AWS Billing / Cost Explorer để kiểm tra các service có thể còn chi phí:

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

Nên kiểm tra lại sau 24 giờ vì một số metric billing có độ trễ.

## Tóm Tắt Lệnh Destroy Chính

Đây là bản rút gọn. Chỉ chạy sau khi đã đọc các cảnh báo và bước empty bucket ở trên.

```bash
cd terraform/8_enterprise && terraform destroy && cd ../..
cd terraform/7_frontend && terraform destroy && cd ../..
cd terraform/6_agents && terraform destroy && cd ../..
cd terraform/5_database && terraform destroy && cd ../..
cd terraform/4_researcher && terraform destroy && cd ../..
cd terraform/3_ingestion && terraform destroy && cd ../..
cd terraform/2_sagemaker && terraform destroy && cd ../..
```

Nếu bất kỳ bước nào fail, dừng lại, đọc phần Troubleshooting, sửa đúng bước đó, rồi mới tiếp tục bước tiếp theo.
