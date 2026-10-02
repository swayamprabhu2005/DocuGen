"""Cryptographic digital signature module for DocuGen AI.

Provides X.509 certificate generation, tamper-evident digital signing,
and cryptographic verification for generated documents.
"""

from __future__ import annotations

import base64
import datetime
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
from pydantic import BaseModel, Field

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

logger = logging.getLogger("docugen.signing")


class DigitalSignatureConfig(BaseModel):
    """Configuration for document cryptographic digital signing."""

    signer_name: str = "DocuGen Verified Authority"
    organization: str = "DocuGen AI Certification"
    reason: str = "Certified Document Authenticity & Non-Repudiation"
    location: str = "DocuGen Secure Enclave"
    contact_info: Optional[str] = "compliance@docugen.ai"
    private_key_pem: Optional[str] = None
    certificate_pem: Optional[str] = None
    private_key_path: Optional[Union[str, Path]] = None
    certificate_path: Optional[Union[str, Path]] = None
    auto_generate_self_signed: bool = True


def generate_self_signed_certificate(
    common_name: str = "DocuGen Verified Authority",
    organization: str = "DocuGen AI Network",
    country: str = "US",
    validity_days: int = 365,
) -> Tuple[bytes, bytes]:
    """Generate a 2048-bit RSA private key and self-signed X.509 certificate in PEM format.

    Returns:
        Tuple[bytes, bytes]: (private_key_pem, certificate_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ]
    )

    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=validity_days))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(private_key, hashes.SHA256())
    )

    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    cert_pem = cert.public_bytes(serialization.Encoding.PEM)

    return priv_pem, cert_pem


def sign_pdf_document(
    pdf_path: Path,
    config: Optional[DigitalSignatureConfig] = None,
) -> Path:
    """Apply cryptographic digital signature to a generated PDF file.

    Computes SHA-256 digest of original PDF bytes, signs with RSA private key,
    and appends a standardized cryptographic signature block.

    Args:
        pdf_path: Path to existing PDF file.
        config: DigitalSignatureConfig instance.

    Returns:
        Path: Path to signed PDF file.
    """
    cfg = config or DigitalSignatureConfig()
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file to sign does not exist: {pdf_path}")

    # Read original document bytes
    original_bytes = pdf_file.read_bytes()

    # Resolve or generate credentials
    priv_pem_bytes: bytes
    cert_pem_bytes: bytes

    if cfg.private_key_pem and cfg.certificate_pem:
        priv_pem_bytes = cfg.private_key_pem.encode("utf-8")
        cert_pem_bytes = cfg.certificate_pem.encode("utf-8")
    elif cfg.private_key_path and cfg.certificate_path:
        priv_pem_bytes = Path(cfg.private_key_path).read_bytes()
        cert_pem_bytes = Path(cfg.certificate_path).read_bytes()
    elif cfg.auto_generate_self_signed:
        priv_pem_bytes, cert_pem_bytes = generate_self_signed_certificate(
            common_name=cfg.signer_name,
            organization=cfg.organization,
        )
    else:
        raise ValueError("No private key or certificate provided and auto_generate_self_signed is False.")

    # Load private key
    private_key = serialization.load_pem_private_key(priv_pem_bytes, password=None)

    # Compute document SHA-256 digest
    hasher = hashlib.sha256()
    hasher.update(original_bytes)
    doc_digest = hasher.hexdigest()

    # Sign digest with RSA-PKCS1v15 + SHA256
    signature_bytes = private_key.sign(
        hasher.digest(),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    sig_hex = signature_bytes.hex()
    cert_b64 = base64.b64encode(cert_pem_bytes).decode("ascii")

    # Construct signature metadata payload
    timestamp_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    meta = {
        "signer": cfg.signer_name,
        "organization": cfg.organization,
        "reason": cfg.reason,
        "location": cfg.location,
        "timestamp": timestamp_utc,
        "digest_algo": "SHA-256",
        "document_digest": doc_digest,
        "signature_algo": "RSA-PKCS1v15-SHA256",
        "signature": sig_hex,
        "certificate_b64": cert_b64,
    }

    meta_json = json.dumps(meta)
    sig_block = (f"\n%%DOCUGEN_DIGITAL_SIGNATURE_START\n%{meta_json}\n%%DOCUGEN_DIGITAL_SIGNATURE_END\n").encode(
        "utf-8"
    )

    # Append signature block to PDF
    signed_bytes = original_bytes + sig_block
    pdf_file.write_bytes(signed_bytes)

    logger.info("Successfully signed PDF %s with signer '%s'", pdf_file.name, cfg.signer_name)
    return pdf_file


def verify_pdf_signature(pdf_path_or_bytes: Union[str, Path, bytes]) -> Dict[str, Any]:
    """Verify cryptographic authenticity and tamper-resistance of a signed PDF.

    Args:
        pdf_path_or_bytes: Path to PDF file, path string, or raw PDF bytes.

    Returns:
        Dict[str, Any]: Verification status, diagnostics, and signature details.
    """
    if isinstance(pdf_path_or_bytes, bytes):
        content = pdf_path_or_bytes
    else:
        pdf_file = Path(pdf_path_or_bytes)
        if not pdf_file.exists():
            return {"valid": False, "error": f"File does not exist: {pdf_path_or_bytes}"}
        content = pdf_file.read_bytes()

    marker_start = b"\n%%DOCUGEN_DIGITAL_SIGNATURE_START\n%"
    marker_end = b"\n%%DOCUGEN_DIGITAL_SIGNATURE_END"

    start_idx = content.find(marker_start)
    end_idx = content.find(marker_end)

    if start_idx == -1 or end_idx == -1:
        return {
            "valid": False,
            "signed": False,
            "error": "No DocuGen digital signature found in document.",
        }

    # Extract original bytes and metadata
    original_bytes = content[:start_idx]
    meta_start = start_idx + len(marker_start)
    meta_json_bytes = content[meta_start:end_idx].strip()

    try:
        meta = json.loads(meta_json_bytes.decode("utf-8"))
    except Exception as exc:
        return {"valid": False, "signed": True, "error": f"Corrupt signature metadata: {exc}"}

    # Verify SHA-256 digest
    calc_hasher = hashlib.sha256()
    calc_hasher.update(original_bytes)
    calc_digest = calc_hasher.hexdigest()

    expected_digest = meta.get("document_digest")
    if calc_digest != expected_digest:
        return {
            "valid": False,
            "signed": True,
            "error": "Document has been modified or tampered with since signing (digest mismatch).",
            "metadata": meta,
        }

    # Verify RSA signature with certificate
    try:
        cert_pem = base64.b64decode(meta["certificate_b64"])
        cert = x509.load_pem_x509_certificate(cert_pem)
        pub_key = cert.public_key()
        sig_bytes = bytes.fromhex(meta["signature"])

        pub_key.verify(
            sig_bytes,
            calc_hasher.digest(),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )

        return {
            "valid": True,
            "signed": True,
            "signer": meta.get("signer"),
            "organization": meta.get("organization"),
            "reason": meta.get("reason"),
            "timestamp": meta.get("timestamp"),
            "digest": calc_digest,
            "certificate_subject": cert.subject.rfc4514_string(),
            "not_valid_after": cert.not_valid_after_utc.isoformat(),
        }
    except Exception as exc:
        return {
            "valid": False,
            "signed": True,
            "error": f"Cryptographic signature verification failed: {exc}",
            "metadata": meta,
        }
