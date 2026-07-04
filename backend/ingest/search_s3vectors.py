# File này là Lambda handler phục vụ semantic search trên S3 Vectors.
# Vai trò của nó ngược với ingest_s3vectors.py.
# Thay vì ghi dữ liệu, file này nhận câu truy vấn, biến truy vấn thành embedding,
# rồi gọi query_vectors để lấy ra các vector gần nhất về mặt ngữ nghĩa.
# Kết quả trả về được format thành JSON đơn giản để API hoặc service khác dễ dùng.
"""
Lambda function for searching S3 Vectors.
"""

import json
# Import json để encode/decode payload khi làm việc với SageMaker và response HTTP.
import os
# Import os để đọc biến môi trường cấu hình bucket, endpoint và index.
import boto3
# Import boto3 để tạo client AWS cho SageMaker và S3 Vectors.

# Các biến môi trường xác định bucket vector, endpoint embedding, và tên index.
# Nhờ đó cùng một Lambda có thể chạy ổn trên nhiều account/region mà không hard-code.
# Environment variables
VECTOR_BUCKET = os.environ.get('VECTOR_BUCKET', 'alex-vectors')
# Đọc bucket sẽ dùng để truy vấn vector.
SAGEMAKER_ENDPOINT = os.environ.get('SAGEMAKER_ENDPOINT')
# Đọc endpoint embedding để vector hóa câu truy vấn.
INDEX_NAME = os.environ.get('INDEX_NAME', 'financial-research')
# Đọc tên index semantic search; mặc định khớp với guide.

# Tạo client một lần ở mức module để tận dụng warm start của Lambda.
# Initialize AWS clients
sagemaker_runtime = boto3.client('sagemaker-runtime')
# Client dùng để gọi model embedding.
s3_vectors = boto3.client('s3vectors')
# Client dùng để query vector trong S3 Vectors.


# Hàm phụ trách chuyển câu truy vấn text thành vector embedding.
# Cấu trúc phản hồi của Hugging Face container có thể lồng nhiều lớp list,
# nên phần xử lý phía dưới bóc tách về đúng mảng float 1 chiều trước khi query.
def get_embedding(text):
    """Get embedding vector from SageMaker endpoint."""
    response = sagemaker_runtime.invoke_endpoint(
        # Gọi endpoint embedding của SageMaker.
        EndpointName=SAGEMAKER_ENDPOINT,
        # Chỉ rõ tên endpoint cần invoke.
        ContentType='application/json',
        # Báo rằng payload đang được gửi lên dưới dạng JSON.
        Body=json.dumps({'inputs': text})
        # Đóng gói câu truy vấn theo đúng format container Hugging Face yêu cầu.
    )
    
    result = json.loads(response['Body'].read().decode())
    # Đọc và parse kết quả SageMaker trả về sang object Python.
    # HuggingFace returns nested array [[[embedding]]], extract the actual embedding
    if isinstance(result, list) and len(result) > 0:
        # Bước 1: kiểm tra response là list không rỗng.
        if isinstance(result[0], list) and len(result[0]) > 0:
            # Bước 2: kiểm tra lớp lồng tiếp theo để tránh index lỗi.
            if isinstance(result[0][0], list):
                # Nếu còn lồng thêm một lớp nữa thì response có dạng [[[embedding]]].
                return result[0][0]  # Extract from [[[embedding]]]
                # Lấy đúng mảng embedding 1 chiều ra khỏi lớp lồng thứ ba.
            return result[0]  # Extract from [[embedding]]
            # Nếu response chỉ có 2 lớp thì trả phần tử đầu.
    return result  # Return as-is if not nested
    # Nếu response không lồng thì trả nguyên để giữ tính tương thích và hỗ trợ debug.


# Đây là Lambda handler cho chức năng search.
# Nó nhận body chứa query và tham số k,
# gọi model embedding để vector hóa query,
# rồi truy vấn S3 Vectors và đóng gói lại kết quả trả về.
# File này không tự đổi distance sang similarity; nó giữ nguyên distance trong response.
def lambda_handler(event, context):
    """
    Search handler.
    Expects JSON body with:
    {
        "query": "Search query text",
        "k": 5  # Optional, defaults to 5
    }
    """
    # Parse the request body
    if isinstance(event.get('body'), str):
        # Nếu API Gateway gửi body ở dạng chuỗi JSON thì cần parse.
        body = json.loads(event['body'])
        # Chuyển string JSON thành dict Python.
    else:
        # Nếu body đã là object thì dùng trực tiếp.
        body = event.get('body', {})
        # Nếu body không tồn tại thì fallback về dict rỗng.
    
    query_text = body.get('query')
    # Lấy câu truy vấn semantic search từ payload.
    k = body.get('k', 5)
    # Lấy topK; nếu client không truyền thì mặc định lấy 5 kết quả.
    
    if not query_text:
        # Nếu không có query thì không thể vector hóa và truy vấn.
        return {
            # Trả response lỗi đầu vào theo format HTTP-style.
            'statusCode': 400,
            # Báo lỗi client side do thiếu trường bắt buộc.
            'body': json.dumps({'error': 'Missing required field: query'})
            # Đóng gói thông điệp lỗi thành JSON.
        }
    
    # Get embedding for query
    print(f"Getting embedding for query: {query_text}")
    # Ghi log query đang được vector hóa để tiện theo dõi trên CloudWatch.
    query_embedding = get_embedding(query_text)
    # Sinh embedding cho câu truy vấn người dùng.
    
    # Search S3 Vectors
    print(f"Searching in bucket: {VECTOR_BUCKET}, index: {INDEX_NAME}")
    # Ghi log bucket và index đang được dùng để query.
    response = s3_vectors.query_vectors(
        # Gọi API truy vấn vector gần nhất theo embedding vừa sinh.
        vectorBucketName=VECTOR_BUCKET,
        # Chỉ rõ bucket vector cần truy vấn.
        indexName=INDEX_NAME,
        # Chỉ rõ index semantic search bên trong bucket.
        queryVector={"float32": query_embedding},
        # Truyền embedding truy vấn dưới dạng float32 đúng chuẩn.
        topK=k,
        # Yêu cầu tối đa k kết quả phù hợp nhất.
        returnDistance=True,
        # Yêu cầu trả cả khoảng cách để client có thể tự tính similarity nếu muốn.
        returnMetadata=True
        # Yêu cầu trả metadata để biết text và thông tin gắn với vector.
    )
    
    # Format results
    results = []
    # Khởi tạo danh sách kết quả đã được chuẩn hóa cho response cuối.
    for vector in response.get('vectors', []):
        # Duyệt qua từng vector match mà S3 Vectors trả về.
        results.append({
            # Chuẩn hóa một vector match thành object đơn giản hơn.
            'id': vector['key'],
            # Lấy key của vector làm id phản hồi.
            'score': vector.get('distance', 0),
            # Ở implementation này score thực ra đang là distance gốc do AWS trả về.
            'text': vector.get('metadata', {}).get('text', ''),
            # Lấy text gốc từ metadata để hiển thị hoặc debug.
            'metadata': vector.get('metadata', {})
            # Giữ nguyên toàn bộ metadata để client dùng thêm nếu cần.
        })
    
    return {
        # Trả response HTTP 200 khi truy vấn hoàn tất thành công.
        'statusCode': 200,
        # Khai báo trạng thái thành công.
        'body': json.dumps({
            # Body trả về là JSON chứa danh sách kết quả và tổng số lượng.
            'results': results,
            # Danh sách match đã được chuẩn hóa.
            'count': len(results)
            # Tổng số kết quả thực tế đang trả về cho client.
        })
    }
