# File này là Lambda handler chính của Part 3.
# Nhiệm vụ của nó là nhận văn bản từ API Gateway hoặc từ event nội bộ.
# Sau đó file sẽ gọi SageMaker Endpoint để biến văn bản thành embedding 384 chiều.
# Cuối cùng embedding và metadata sẽ được ghi vào S3 Vectors index.
# Đây là mắt xích trung tâm nối giữa lớp API ingest và kho vector search.
"""
Lambda function for ingesting text into S3 Vectors with embeddings.
"""

import json
# Import json để encode payload gửi sang SageMaker và decode response trả về.
import os
# Import os để đọc biến môi trường do Terraform truyền vào Lambda.
import boto3
# Import boto3 để tạo client giao tiếp với các dịch vụ AWS.
import datetime
# Import datetime để đóng dấu thời gian khi lưu metadata.
import uuid
# Import uuid để tạo khóa định danh duy nhất cho từng vector.

# Nhóm biến môi trường này cho phép cùng một file code chạy được ở nhiều môi trường.
# Terraform sẽ truyền giá trị thật vào khi deploy Lambda.
# Nếu thiếu INDEX_NAME thì code mặc định dùng financial-research theo đúng guide.
# Environment variables
VECTOR_BUCKET = os.environ.get('VECTOR_BUCKET', 'alex-vectors')
# Đọc tên bucket vector từ biến môi trường; nếu thiếu thì dùng giá trị mặc định an toàn cho local.
SAGEMAKER_ENDPOINT = os.environ.get('SAGEMAKER_ENDPOINT')
# Đọc tên endpoint embedding để biết phải gọi model nào ở Part 2.
INDEX_NAME = os.environ.get('INDEX_NAME', 'financial-research')
# Đọc tên index semantic search; mặc định là financial-research theo hướng dẫn khóa học.

# Hai client boto3 được tạo một lần ở mức module để Lambda có thể tái sử dụng.
# Cách này giúp warm start nhanh hơn vì không phải tạo lại client ở mỗi request.
# Initialize AWS clients
sagemaker_runtime = boto3.client('sagemaker-runtime')
# Tạo client chuyên dùng để invoke SageMaker endpoint sinh embedding.
s3_vectors = boto3.client('s3vectors')
# Tạo client chuyên dùng để ghi dữ liệu vector vào S3 Vectors.


# Hàm này cô lập toàn bộ logic gọi mô hình embedding.
# Đầu vào là một chuỗi text bất kỳ; đầu ra kỳ vọng là list số thực 1 chiều.
# Việc tách riêng giúp lambda_handler gọn hơn và tái sử dụng được ở nhiều script khác.
def get_embedding(text):
    """Get embedding vector from SageMaker endpoint."""
    response = sagemaker_runtime.invoke_endpoint(
        # Gọi endpoint inference của SageMaker bằng client đã khởi tạo sẵn.
        EndpointName=SAGEMAKER_ENDPOINT,
        # Truyền tên endpoint embedding lấy từ biến môi trường.
        ContentType='application/json',
        # Báo cho container biết payload đầu vào có định dạng JSON.
        Body=json.dumps({'inputs': text})
        # Đóng gói văn bản thành JSON theo format mà Hugging Face container mong đợi.
    )
    
    result = json.loads(response['Body'].read().decode())
    # Đọc body nhị phân từ SageMaker, decode sang chuỗi rồi parse thành object Python.
    # HuggingFace returns nested array [[[embedding]]], extract the actual embedding
    if isinstance(result, list) and len(result) > 0:
        # Kiểm tra response có phải list không rỗng hay không trước khi truy cập phần tử.
        if isinstance(result[0], list) and len(result[0]) > 0:
            # Kiểm tra lớp lồng thứ hai để tránh lỗi index hoặc sai định dạng.
            if isinstance(result[0][0], list):
                # Nếu phần tử cấp 3 vẫn là list thì response có dạng [[[embedding]]].
                return result[0][0]  # Extract from [[[embedding]]]
                # Bóc đúng vector 1 chiều từ cấu trúc 3 lớp.
            return result[0]  # Extract from [[embedding]]
            # Nếu chỉ lồng 2 lớp thì lấy phần tử đầu làm embedding.
    return result  # Return as-is if not nested
    # Nếu response không lồng như kỳ vọng thì trả nguyên giá trị để tiện debug.


# Đây là điểm vào chuẩn của AWS Lambda.
# Hàm này chịu trách nhiệm:
# 1. đọc payload từ event,
# 2. kiểm tra trường text bắt buộc,
# 3. sinh embedding,
# 4. tạo khóa định danh duy nhất,
# 5. lưu vector và metadata vào S3 Vectors,
# 6. trả JSON response theo format HTTP quen thuộc của API Gateway proxy integration.
def lambda_handler(event, context):
    """
    Main Lambda handler.
    Expects JSON body with:
    {
        "text": "Text to ingest",
        "metadata": {
            "source": "optional source",
            "category": "optional category"
        }
    }
    """
    try:
        # Bắt toàn bộ exception để Lambda luôn trả response JSON thay vì crash thô.
        # Parse the request body
        if isinstance(event.get('body'), str):
            # Nếu API Gateway gửi body dạng string JSON thì cần parse trước.
            body = json.loads(event['body'])
            # Chuyển chuỗi JSON sang dict Python.
        else:
            # Nếu body đã là object thì dùng luôn, thường gặp ở test nội bộ.
            body = event.get('body', {})
            # Lấy body nếu có, còn không thì dùng dict rỗng để tránh lỗi.
        
        text = body.get('text')
        # Lấy trường text là nội dung chính cần vector hóa.
        metadata = body.get('metadata', {})
        # Lấy metadata nếu có; nếu không truyền thì dùng dict rỗng.
        
        if not text:
            # Nếu thiếu text thì request không hợp lệ vì không có gì để embedding.
            return {
                # Trả về object response theo format HTTP-style của Lambda proxy.
                'statusCode': 400,
                # Báo client biết đây là lỗi đầu vào không hợp lệ.
                'body': json.dumps({'error': 'Missing required field: text'})
                # Đưa thông báo lỗi vào body JSON để client dễ đọc.
            }
        
        # Get embedding from SageMaker
        print(f"Getting embedding for text: {text[:100]}...")
        # Ghi log đoạn đầu của text để dễ debug mà không in toàn bộ nội dung quá dài.
        embedding = get_embedding(text)
        # Gọi hàm phụ để lấy embedding 1 chiều từ SageMaker.
        
        # Generate unique ID for the vector
        vector_id = str(uuid.uuid4())
        # Tạo UUID ngẫu nhiên để làm khóa duy nhất cho vector trong index.
        
        # Store in S3 Vectors
        print(f"Storing vector in bucket: {VECTOR_BUCKET}, index: {INDEX_NAME}")
        # Ghi log bucket và index đích để thuận tiện kiểm tra môi trường đang chạy.
        s3_vectors.put_vectors(
            # Gọi API put_vectors để ghi vector mới vào index.
            vectorBucketName=VECTOR_BUCKET,
            # Chỉ rõ bucket vector cần ghi vào.
            indexName=INDEX_NAME,
            # Chỉ rõ index semantic search bên trong bucket.
            vectors=[{
                # put_vectors nhận danh sách vector; ở đây ta ghi 1 vector mỗi request.
                "key": vector_id,
                # Khóa định danh duy nhất của vector trong index.
                "data": {"float32": embedding},
                # Dữ liệu embedding được gửi dưới kiểu float32 mà S3 Vectors mong đợi.
                "metadata": {
                    # Metadata cho phép lưu text gốc và thông tin phụ để search/debug.
                    "text": text,
                    # Lưu lại văn bản gốc phục vụ truy xuất ngữ cảnh sau này.
                    "timestamp": datetime.datetime.utcnow().isoformat(),
                    # Gắn thời điểm ingest theo UTC để tiện audit và sắp xếp.
                    **metadata  # Include any additional metadata
                    # Trộn thêm metadata do client gửi lên như source hoặc category.
                }
            }]
        )
        
        return {
            # Nếu mọi thứ thành công thì trả về phản hồi HTTP 200.
            'statusCode': 200,
            # Khai báo status code thành công.
            'body': json.dumps({
                # Body trả về là JSON để client dùng trực tiếp.
                'message': 'Document indexed successfully',
                # Thông điệp xác nhận rằng văn bản đã được ghi vào index.
                'document_id': vector_id
                # Trả lại ID vừa sinh để client có thể trace hoặc lưu tham chiếu.
            })
        }
    except Exception as e:
        # Nếu bất kỳ bước nào lỗi thì ghi log và trả 500 thay vì để Lambda ném exception trần.
        print(f"Error: {str(e)}")
        # In thông điệp lỗi ra CloudWatch Logs để debug.
        return {
            # Trả về response lỗi phía server.
            'statusCode': 500,
            # Khai báo đây là lỗi nội bộ trong quá trình xử lý.
            'body': json.dumps({'error': str(e)})
            # Đưa thông điệp lỗi vào body JSON để quan sát nhanh khi test.
        }
