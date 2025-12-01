
class AuthError(Exception):
    """ベース認証エラー"""
    pass

class UnauthorizedError(AuthError):
    """認証失敗 (401 Unauthorized)"""
    def __init__(self, message="Authentication failed"):
        self.message = message
        super().__init__(self.message)

class ForbiddenError(AuthError):
    """アクセス拒否 (403 Forbidden)"""
    def __init__(self, message="Access forbidden"):
        self.message = message
        super().__init__(self.message)

class ServiceUnavailableError(AuthError):
    """外部サービス利用不可 (503 Service Unavailable)"""
    def __init__(self, message="External service temporarily unavailable"):
        self.message = message
        super().__init__(self.message)
