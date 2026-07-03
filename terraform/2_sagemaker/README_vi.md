# Giải thích folder `terraform/2_sagemaker`

File này giải thích dễ hiểu toàn bộ nhiệm vụ của folder `terraform/2_sagemaker`, các file bên trong, và cách chúng phối hợp với nhau.

## 1. Mục tiêu của folder này là gì?

Folder `terraform/2_sagemaker` dùng để deploy **SageMaker Serverless Endpoint** cho project Alex.

Endpoint này có nhiệm vụ:

- nhận text đầu vào;
- biến text thành **vector embedding**;
- trả về mảng số thực để các bước sau dùng cho semantic search / RAG.

Trong project Alex, đây là "nhà máy tạo vector".

Sau này:

- `Guide 3` sẽ gọi endpoint này từ Lambda ingest;
- vector tạo ra sẽ được đưa vào `S3 Vectors`.

## 2. Folder này tạo ra những gì trên AWS?

Khi chạy `terraform apply`, folder này tạo các resource chính sau:

1. **IAM Role**  
   SageMaker cần một role để được phép chạy model trong tài khoản AWS của bạn.

2. **SageMaker Model**  
   Đây là phần khai báo model inference, nói cho SageMaker biết:
   - dùng container nào;
   - tải model nào từ Hugging Face;
   - task là gì.

3. **SageMaker Endpoint Configuration**  
   Cấu hình cách endpoint sẽ chạy:
   - serverless;
   - memory bao nhiêu;
   - cho phép bao nhiêu request đồng thời.

4. **SageMaker Endpoint**  
   Đây là endpoint thực tế mà backend, CLI, hoặc Lambda sẽ gọi đến để sinh embeddings.

5. **Time Sleep**  
   Đây không phải tài nguyên nghiệp vụ, mà là workaround để tránh lỗi IAM propagation.

## 3. Giải thích từng file trong folder

### `main.tf`

Đây là file trung tâm.

Nó định nghĩa:

- provider AWS;
- IAM role cho SageMaker;
- SageMaker model;
- endpoint configuration;
- endpoint;
- `time_sleep` để chờ IAM propagate.

Nếu bạn muốn hiểu "folder này thực sự tạo resource gì", hãy đọc file này đầu tiên.

### `variables.tf`

File này khai báo các **input variables** cho folder này.

Hiện tại có 3 biến chính:

- `aws_region`: region deploy SageMaker;
- `sagemaker_image_uri`: URI của Hugging Face inference container trên ECR;
- `embedding_model_name`: tên model embedding trên Hugging Face Hub.

File này không thực hiện deploy. Nó chỉ định nghĩa "folder này cần nhận đầu vào nào".

### `outputs.tf`

File này khai báo những giá trị cần in ra sau khi deploy xong.

Quan trọng nhất là:

- `sagemaker_endpoint_name`;
- `sagemaker_endpoint_arn`.

Giá trị `sagemaker_endpoint_name` sẽ được copy vào `.env`:

```env
SAGEMAKER_ENDPOINT=alex-embedding-endpoint
```

### `terraform.tfvars.example`

Đây là file mẫu.

Bạn sẽ:

1. copy nó thành `terraform.tfvars`;
2. sửa giá trị cho đúng máy của bạn.

Mục đích:

- tránh sửa trực tiếp vào `variables.tf`;
- tách "default của code" và "giá trị thực tế của người dùng".

### `terraform.tfvars`

File này thường do bạn tự tạo từ file example.

Nó chứa giá trị thực tế cho lần deploy của bạn, ví dụ:

```hcl
aws_region = "ap-southeast-1"
sagemaker_image_uri = "763104351884.dkr.ecr.ap-southeast-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04"
```

File này rất quan trọng vì mỗi học viên có thể deploy ở region khác nhau.

### `.terraform.lock.hcl`

File này được Terraform tạo ra để khóa version provider.

Nó giúp:

- lần sau vẫn dùng cùng version provider;
- hạn chế lỗi do version thay đổi bất ngờ.

Thường không cần sửa tay.

### `.terraform/`

Thư mục này do Terraform tạo ra khi chạy `terraform init`.

Nó chứa:

- binary provider;
- metadata cần cho Terraform chạy.

Thường không cần sửa tay.

### `terraform.tfstate`

File này sẽ xuất hiện sau khi apply thành công.

Nó là "bộ nhớ" của Terraform, ghi lại:

- đã tạo resource nào;
- resource đó có ID/ARN gì;
- lần sau cần update hay destroy cái gì.

Rất quan trọng:

- mất file state có thể khiến Terraform "quên" resource đã tạo;
- khi đó dễ gặp lỗi resource đã tồn tại nhưng Terraform không quản lý.

## 4. Luồng hoạt động của folder này

Đây là cách các file và resource phối hợp:

1. Bạn set giá trị trong `terraform.tfvars`.
2. `provider "aws"` dùng `aws_region`.
3. Terraform tạo IAM role.
4. Terraform gắn `AmazonSageMakerFullAccess` vào role.
5. Terraform tạo `aws_sagemaker_model`.
6. Terraform tạo `aws_sagemaker_endpoint_configuration`.
7. Terraform chờ 15 giây để IAM propagate.
8. Terraform tạo `aws_sagemaker_endpoint`.
9. `outputs.tf` in ra tên endpoint và ARN.

## 5. Giải thích dễ hiểu về model và container

Nhiều bạn hay nhầm chỗ này.

Cần tách rõ:

### `embedding_model_name`

Đây là model trên Hugging Face Hub:

`sentence-transformers/all-MiniLM-L6-v2`

Nó quyết định:

- model nào được tải về;
- embedding có kích thước bao nhiêu.

Model này trả về vector **384 chiều**.

### `sagemaker_image_uri`

Đây không phải model.

Đây là **container image** mà SageMaker sẽ chạy.

Container này biết cách:

- nhận request JSON;
- tải model từ Hugging Face;
- chạy inference;
- trả về kết quả.

Nó giống như "bộ máy chạy model", còn `embedding_model_name` là "model cụ thể được nạp vào bộ máy đó".

## 6. Vì sao lỗi region xảy ra?

Lỗi bạn vừa gặp là:

`Cross region ECR image pulls are not allowed`

Nghĩa dễ hiểu:

- SageMaker đang được tạo ở một region, ví dụ `ap-southeast-1`;
- nhưng container image lại đang trỏ tới ECR ở region khác, ví dụ `us-east-1`.

SageMaker không cho kéo image ECR xuyên region trong trường hợp này.

Nên quy tắc là:

- `aws_region` là gì;
- `sagemaker_image_uri` cũng phải ở region đó.

Ví dụ:

```hcl
aws_region = "ap-southeast-1"
sagemaker_image_uri = "763104351884.dkr.ecr.ap-southeast-1.amazonaws.com/huggingface-pytorch-inference:1.13.1-transformers4.26.0-cpu-py39-ubuntu20.04"
```

## 7. Vì sao cần `time_sleep`?

AWS IAM không phải lúc nào cũng có hiệu lực ngay lập tức.

Có trường hợp:

1. Terraform vừa tạo role.
2. Terraform vừa gắn policy xong.
3. SageMaker lập tức dùng role đó.
4. AWS báo role chưa hợp lệ.

Lý do không phải do role sai, mà do **IAM propagation delay**.

`time_sleep` 15 giây giải quyết đúng vấn đề này.

## 8. Vì sao dùng serverless?

Folder này chọn **SageMaker Serverless Endpoint** thay vì always-on endpoint vì:

- dễ học nhanh;
- không cần quản lý server;
- có thể scale-to-zero;
- chi phí thấp hơn cho môi trường học tập / dev.

Trade-off:

- request đầu tiên có thể chậm hơn do **cold start**.

## 9. Các lệnh thường dùng trong folder này

### Khởi tạo Terraform

```bash
terraform init
```

### Xem Terraform sẽ tạo gì

```bash
terraform plan
```

### Deploy resource

```bash
terraform apply
```

### Xem output sau khi deploy

```bash
terraform output
```

### Xóa resource của riêng guide này

```bash
terraform destroy
```

## 10. Sau khi deploy xong cần làm gì?

Có 3 việc chính:

1. Copy endpoint name vào `.env`.
2. Check endpoint đã `InService`.
3. Test invoke endpoint.

Ví dụ:

```bash
aws sagemaker describe-endpoint \
  --endpoint-name alex-embedding-endpoint \
  --region ap-southeast-1
```

Và test:

```bash
cd ../../backend
aws sagemaker-runtime invoke-endpoint \
  --endpoint-name alex-embedding-endpoint \
  --content-type application/json \
  --body fileb://vectorize_me.json \
  --output json /dev/stdout \
  --region ap-southeast-1
```

## 11. Nếu có lỗi thì check gì trước?

### Trường hợp 1: Lỗi region ECR

Check:

- `aws_region`;
- `sagemaker_image_uri`.

Hai giá trị này phải cùng region.

### Trường hợp 2: Lỗi role invalid / cannot be assumed

Check:

- có `time_sleep` không;
- apply lại sau một lúc.

### Trường hợp 3: Endpoint tạo lâu

Đây là bình thường.

Serverless endpoint của SageMaker có thể mất vài phút để khởi tạo.

### Trường hợp 4: Invoke không thấy endpoint

Thường là do AWS CLI đang dùng default region khác region deploy.

Fix:

- thêm `--region ap-southeast-1` vào lệnh invoke.

## 12. Tóm tắt ngắn gọn

Nếu phải nhớ ngắn gọn về folder này, chỉ cần nhớ:

- `main.tf` = định nghĩa resource;
- `variables.tf` = khai báo input;
- `terraform.tfvars` = giá trị thực tế;
- `outputs.tf` = giá trị lấy ra sau deploy;
- `terraform.tfstate` = bộ nhớ của Terraform.

Và quy tắc quan trọng nhất của guide này:

**Region của SageMaker và region của ECR image phải khớp nhau.**
