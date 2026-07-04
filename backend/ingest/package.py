#!/usr/bin/env python3
# Shebang này cho phép chạy script trực tiếp trên các môi trường hỗ trợ Python executable.
# File này chịu trách nhiệm đóng gói mã nguồn Lambda và dependencies thành file zip.
# Đây là bước chuẩn bị artifact để Terraform ở Part 3 có thể upload code lên AWS Lambda.
# Script được viết theo hướng cross-platform để học viên trên Windows, macOS, Linux đều dùng được.
"""
Cross-platform Lambda deployment package creator using uv.
Works on Windows, Mac, and Linux.
"""

import os
# Import os để duyệt cây thư mục và xóa file khi đóng gói.
import sys
# Import sys để thoát chương trình bằng exit code khi gặp lỗi cấu hình.
import shutil
# Import shutil để copy thư mục/file và xóa thư mục build tạm.
import zipfile
# Import zipfile để tạo deployment package ở định dạng .zip cho Lambda.
from pathlib import Path
# Import Path để thao tác đường dẫn theo kiểu hiện đại và dễ đọc.


# Hàm này tạo deployment package theo đúng cấu trúc Lambda mong đợi.
# Quy trình chính:
# 1. tìm site-packages trong .venv do uv quản lý,
# 2. copy dependencies vào thư mục build/package,
# 3. copy mã nguồn handler,
# 4. nén toàn bộ thành lambda_function.zip,
# 5. dọn thư mục tạm để workspace sạch sẽ.
def create_deployment_package():
    """Create a Lambda deployment package with dependencies from uv."""
    
    # Paths
    current_dir = Path(__file__).parent
    # Xác định thư mục hiện tại của script để tính các đường dẫn khác tương đối từ đây.
    build_dir = current_dir / 'build'
    # Thư mục build là nơi chứa dữ liệu tạm trong lúc đóng gói.
    package_dir = build_dir / 'package'
    # package_dir là thư mục con sẽ chứa đúng nội dung cần zip lên Lambda.
    zip_path = current_dir / 'lambda_function.zip'
    # zip_path là đường dẫn file artifact cuối cùng Terraform sẽ dùng.
    venv_site_packages = current_dir / '.venv' / 'lib'
    # Đây là gốc để dò site-packages bên trong virtual environment do uv tạo ra.
    
    # Clean up previous builds
    if build_dir.exists():
        # Nếu build cũ còn tồn tại thì cần xóa để tránh sót file cũ vào package mới.
        shutil.rmtree(build_dir)
        # Xóa toàn bộ thư mục build cũ.
    if zip_path.exists():
        # Nếu zip cũ còn tồn tại thì cần xóa để tạo artifact sạch từ đầu.
        os.remove(zip_path)
        # Xóa file lambda_function.zip cũ.
    
    # Create build directory
    package_dir.mkdir(parents=True, exist_ok=True)
    # Tạo thư mục package cùng cha của nó nếu chưa tồn tại.
    
    # Find the site-packages directory (cross-platform)
    site_packages = None
    # Khởi tạo biến rỗng để lát nữa gán vị trí site-packages tìm được.
    for path in venv_site_packages.rglob('site-packages'):
        # Dò đệ quy bên trong .venv/lib vì tên version Python có thể khác nhau theo máy.
        site_packages = path
        # Gán thư mục site-packages đầu tiên tìm được.
        break
        # Dừng ngay sau khi tìm thấy vì chỉ cần một thư mục đúng.
    
    if not site_packages or not site_packages.exists():
        # Nếu không tìm thấy site-packages thì môi trường chưa được cài dependencies đúng cách.
        print("Error: Could not find site-packages. Make sure you've run 'uv init' and 'uv add' for dependencies.")
        # In thông báo hướng dẫn xử lý để người học biết cần chuẩn bị gì.
        sys.exit(1)
        # Thoát với mã lỗi để CI hoặc người dùng biết packaging đã thất bại.
    
    print(f"Copying dependencies from {site_packages}...")
    # Thông báo đường dẫn site-packages đang được dùng để copy dependencies.
    # Copy all dependencies to package directory
    for item in site_packages.iterdir():
        # Duyệt qua từng package hoặc file trong site-packages.
        if item.name.endswith('.dist-info') or item.name == '__pycache__':
            # Bỏ qua metadata package và cache vì không cần cho runtime Lambda.
            continue
            # Sang phần tử tiếp theo.
        if item.is_dir():
            # Nếu dependency là thư mục package thì copy nguyên cây thư mục.
            shutil.copytree(item, package_dir / item.name, dirs_exist_ok=True)
            # Sao chép package folder vào package_dir.
        else:
            # Nếu dependency là file đơn thì copy trực tiếp.
            shutil.copy2(item, package_dir)
            # Giữ nguyên metadata file khi copy nếu có thể.
    
    # Copy Lambda function code
    print("Copying Lambda function code...")
    # Thông báo bắt đầu chép source code của handler vào package.
    
    # Copy S3 Vectors Lambda handlers
    if (current_dir / 'ingest_s3vectors.py').exists():
        # Kiểm tra handler ingest có tồn tại hay không trước khi copy.
        shutil.copy(current_dir / 'ingest_s3vectors.py', package_dir)
        # Chép file ingest chính vào package Lambda.
    if (current_dir / 'search_s3vectors.py').exists():
        # Kiểm tra handler search có tồn tại hay không trước khi copy.
        shutil.copy(current_dir / 'search_s3vectors.py', package_dir)
        # Chép thêm file search để package có thể dùng cho nhiều handler liên quan.
    
    # Create ZIP file
    print("Creating deployment package...")
    # Thông báo bắt đầu bước nén toàn bộ package thành file zip cuối.
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Mở file zip ở chế độ ghi mới với thuật toán nén deflate.
        for root, dirs, files in os.walk(package_dir):
            # Duyệt đệ quy toàn bộ cây thư mục package đã chuẩn bị.
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']
            # Loại __pycache__ ra khỏi danh sách thư mục sẽ duyệt tiếp.
            for file in files:
                # Duyệt qua từng file cụ thể sẽ được đưa vào zip.
                if file.endswith('.pyc'):
                    # Bỏ qua file bytecode vì Lambda không cần chúng trong package.
                    continue
                    # Chuyển sang file tiếp theo.
                file_path = Path(root) / file
                # Tạo đường dẫn tuyệt đối/tương đối đầy đủ tới file hiện tại.
                arcname = file_path.relative_to(package_dir)
                # Tính tên đường dẫn bên trong file zip để không mang theo prefix build/package.
                zipf.write(file_path, arcname)
                # Ghi file vào zip với tên nội bộ đã chuẩn hóa.
    
    # Clean up build directory
    shutil.rmtree(build_dir)
    # Xóa thư mục build tạm sau khi đã có zip hoàn chỉnh để workspace gọn lại.
    
    # Get file size
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    # Tính kích thước zip theo đơn vị MB để người dùng kiểm tra nhanh.
    print(f"\n✅ Deployment package created: {zip_path}")
    # In đường dẫn artifact vừa tạo thành công.
    print(f"   Size: {size_mb:.2f} MB")
    # In kích thước artifact để so sánh với giới hạn package của Lambda.
    
    if size_mb > 50:
        # Nếu zip quá lớn thì cảnh báo vì dễ đụng giới hạn hoặc gây deploy chậm.
        print("⚠️  Warning: Package exceeds 50MB. Consider using Lambda Layers.")
        # Gợi ý dùng Lambda Layers khi package phình quá mức.
    
    return str(zip_path)
    # Trả về đường dẫn file zip để script khác có thể tái sử dụng nếu cần.


if __name__ == '__main__':
    # Chỉ chạy packaging khi file được execute trực tiếp, không chạy khi import.
    create_deployment_package()
    # Gọi hàm chính để tạo deployment package.
