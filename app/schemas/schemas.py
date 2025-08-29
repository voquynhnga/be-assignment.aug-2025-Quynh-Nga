from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

# ... các schema khác của bạn như RegisterIn, TokenOut, LoginIn ...

# Dưới đây là schema bạn đang hỏi đến
class OrganizationOut(BaseModel):
    """
    Schema này được dùng để trả về thông tin của một Organization.
    Nó chỉ bao gồm những trường mà chúng ta muốn client thấy.
    """
    id: UUID
    name: str

    # Cấu hình quan trọng để Pydantic có thể đọc dữ liệu
    # từ một đối tượng model của SQLAlchemy
    class Config:
        orm_mode = True