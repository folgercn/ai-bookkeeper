import hashlib

def generate_hash_id(user_id: str, date: str, amount: float, remark: str, payee: str = None) -> str:
    """
    生成去重指纹
    包含 user_id 确保用户间隔离
    """
    # 格式化金额为两位小数以保证一致性
    amount_str = f"{float(amount):.2f}"
    raw = f"{user_id}|{date}|{amount_str}|{remark or ''}|{payee or ''}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()
