{
    "name": "Student Security Extension",
    "version": "1.0",
    "summary": "Module to extend student model with security features",
    "description": "This module adds security features to the student model.",
    "author": "Ibrahim",
    "category": "Education",
    "depends": ["student"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}