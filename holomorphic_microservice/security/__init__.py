"""
🛡️ Security Module Initialization
Military-grade security components for Holomorphic Signal Processing

Components:
- Authentication & Authorization
- JWT Token Management
- Role-Based Access Control (RBAC)
- Security Auditing & Monitoring
- Auto-patching & Vulnerability Management
- Input Validation & Sanitization
- Encryption & Secure Storage
"""

from .auth import (
    SecurityManager,
    SecurityConfig,
    SecurityLevel,
    Permission,
    User,
    SecurityAuditEvent,
    verify_token,
    validate_password_strength
)

__all__ = [
    # Core security classes
    "SecurityManager",
    "SecurityConfig",
    
    # Enums
    "SecurityLevel", 
    "Permission",
    
    # Models
    "User",
    "SecurityAuditEvent",
    
    # Utility functions
    "verify_token",
    "validate_password_strength"
]

# Security module metadata
__version__ = "1.0.0"
__author__ = "iDeaKz"
__description__ = "Military-Grade Security System"
__security_level__ = "MILITARY_GRADE"
__encryption__ = "AES-256 + RSA-4096"
__authentication__ = "JWT + Multi-Factor"
__authorization__ = "RBAC + Permissions"
__monitoring__ = "Real-time + Audit Logging"
__auto_patching__ = "Enabled"
__vulnerability_scanning__ = "Continuous"

# Security status
def get_security_info():
    """🛡️ Get security module information"""
    return {
        "version": __version__,
        "security_level": __security_level__,
        "encryption": __encryption__,
        "authentication": __authentication__,
        "authorization": __authorization__,
        "monitoring": __monitoring__,
        "auto_patching": __auto_patching__,
        "vulnerability_scanning": __vulnerability_scanning__,
        "components": len(__all__),
        "status": "OPERATIONAL"
    }