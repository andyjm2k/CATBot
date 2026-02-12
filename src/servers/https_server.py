"""
HTTPS server for serving the CATBot web interface.
Required for iOS Safari to access Web Audio API and microphone.

This server prioritizes mkcert certificates (trusted) and falls back to
self-signed certificates if mkcert is not available. Works with:
- localhost
- anton.local
- IP addresses on your local network
"""
import http.server
import ssl
import socketserver
import os
import socket
import subprocess
import sys
from pathlib import Path

# Project root (two levels up from src/servers/https_server.py)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Configuration
PORT = 8000
HOST = '0.0.0.0'  # Allow network access
# Default certificate files (will be auto-detected if mkcert certificates exist)
CERT_FILE = 'anton.local+2.pem'
KEY_FILE = 'anton.local+2-key.pem'

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler with CORS headers for cross-origin requests."""
    
    def end_headers(self):
        """Add CORS headers to allow cross-origin requests."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        # Connect to a remote address to determine local IP
        # (doesn't actually send data)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def generate_cert_with_openssl(hostnames, ips):
    """Generate certificate using OpenSSL command line tool."""
    # Create a config file for OpenSSL with SANs
    config_content = f"""[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = Local
L = Local
O = CATBot
CN = anton.local

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = anton.local
IP.1 = 127.0.0.1
"""
    
    # Add IP addresses to SANs
    for idx, ip in enumerate(ips, start=2):
        config_content += f"IP.{idx} = {ip}\n"
    
    # Add additional hostnames
    for idx, hostname in enumerate(hostnames, start=3):
        if hostname not in ['localhost', 'anton.local']:
            config_content += f"DNS.{idx} = {hostname}\n"
    
    # Write config file
    config_file = 'openssl.conf'
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    try:
        # Generate private key
        subprocess.run([
            'openssl', 'genrsa', '-out', KEY_FILE, '2048'
        ], check=True, capture_output=True)
        
        # Generate certificate with SANs
        subprocess.run([
            'openssl', 'req', '-new', '-x509',
            '-key', KEY_FILE,
            '-out', CERT_FILE,
            '-days', '365',
            '-config', config_file,
            '-extensions', 'v3_req'
        ], check=True, capture_output=True)
        
        # Clean up config file
        os.remove(config_file)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ OpenSSL error: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False
    except FileNotFoundError:
        return False

def generate_cert_with_cryptography(hostnames, ips):
    """Generate certificate using Python cryptography library."""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from datetime import datetime, timedelta
        import ipaddress
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Build subject
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CATBot"),
            x509.NameAttribute(NameOID.COMMON_NAME, "anton.local"),
        ])
        
        # Build SAN list
        san_list = [
            x509.DNSName("localhost"),
            x509.DNSName("anton.local"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]
        
        # Add additional hostnames
        for hostname in hostnames:
            if hostname not in ['localhost', 'anton.local']:
                san_list.append(x509.DNSName(hostname))
        
        # Add IP addresses
        for ip in ips:
            try:
                san_list.append(x509.IPAddress(ipaddress.IPv4Address(ip)))
            except ValueError:
                print(f"⚠️  Skipping invalid IP: {ip}")
        
        # Create certificate
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write certificate
        with open(CERT_FILE, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        # Write private key
        with open(KEY_FILE, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"❌ Certificate generation error: {e}")
        return False

def check_mkcert_certificates():
    """Check if mkcert-generated certificates exist in certs/ or project root."""
    import glob
    # Search in certs/ first, then project root
    for search_dir in [_PROJECT_ROOT / "certs", _PROJECT_ROOT]:
        if not search_dir.exists():
            continue
        cert_files = list(search_dir.glob("anton.local*.pem"))
        cert_key_pairs = []
        for cert_path in cert_files:
            if '-key' in cert_path.name:
                continue
            key_path = cert_path.parent / (cert_path.stem + "-key.pem")
            if key_path.exists():
                cert_key_pairs.append((str(cert_path), str(key_path), cert_path.stat().st_mtime))
        if cert_key_pairs:
            cert_key_pairs.sort(key=lambda x: x[2], reverse=True)
            return cert_key_pairs[0][0], cert_key_pairs[0][1]
    return None, None

def check_mkcert_installed():
    """Check if mkcert is installed and available."""
    # Check for mkcert.exe in project root first (local copy)
    local_mkcert = str(_PROJECT_ROOT / 'mkcert.exe')
    if os.path.exists(local_mkcert):
        try:
            result = subprocess.run([local_mkcert, '-version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    
    # Fall back to system PATH
    try:
        result = subprocess.run(['mkcert', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def get_mkcert_command():
    """Get the mkcert command to use (local or system)."""
    local_mkcert = str(_PROJECT_ROOT / 'mkcert.exe')
    if os.path.exists(local_mkcert):
        return local_mkcert
    return 'mkcert'

def generate_mkcert_certificate(hostnames, ips):
    """Generate certificate using mkcert if available."""
    if not check_mkcert_installed():
        return False, None, None
    
    try:
        # Get mkcert command (local or system)
        mkcert_cmd = get_mkcert_command()
        # Build mkcert command with all hostnames and IPs
        cmd = [mkcert_cmd] + hostnames + ips
        
        print(f"🔐 Generating certificate with mkcert...")
        print(f"   Hostnames: {', '.join(hostnames)}")
        print(f"   IPs: {', '.join(ips)}")
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=30,
                              cwd=str(_PROJECT_ROOT))
        
        if result.returncode == 0:
            # mkcert creates files like: anton.local+2.pem, anton.local+2-key.pem
            # Find the newly created certificate
            cert_file, key_file = check_mkcert_certificates()
            if cert_file and key_file:
                print(f"✅ Generated mkcert certificate: {cert_file}")
                return True, cert_file, key_file
            else:
                print("⚠️  mkcert succeeded but certificate files not found")
                return False, None, None
        else:
            print(f"❌ mkcert error: {result.stderr}")
            return False, None, None
            
    except subprocess.TimeoutExpired:
        print("❌ mkcert command timed out")
        return False, None, None
    except Exception as e:
        print(f"❌ mkcert error: {e}")
        return False, None, None

def generate_self_signed_cert():
    """Check for mkcert certificates first, then generate self-signed as fallback."""
    global CERT_FILE, KEY_FILE
    
    # First, check for existing mkcert certificates
    mkcert_cert, mkcert_key = check_mkcert_certificates()
    if mkcert_cert and mkcert_key:
        print(f"✅ Found existing mkcert certificate: {mkcert_cert}")
        print("   Make sure mkcert CA is installed: mkcert -install")
        CERT_FILE = mkcert_cert
        KEY_FILE = mkcert_key
        return True
    
    # Check if the configured certificate files exist in certs/ or project root
    for base in [_PROJECT_ROOT / "certs", _PROJECT_ROOT]:
        cert_path = base / CERT_FILE
        key_path = base / KEY_FILE
        if cert_path.exists() and key_path.exists():
            CERT_FILE = str(cert_path)
            KEY_FILE = str(key_path)
            print(f"✅ Using existing certificate: {CERT_FILE}")
            return True
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        print(f"✅ Using existing certificate: {CERT_FILE}")
        # Verify it's a valid certificate file
        try:
            with open(CERT_FILE, 'r') as f:
                content = f.read()
                if 'mkcert' in content.lower() or 'BEGIN CERTIFICATE' in content:
                    print("   Certificate appears to be valid")
                    return True
        except Exception:
            pass
    
    # Try to generate with mkcert if it's installed
    local_ip = get_local_ip()
    hostnames = ['anton.local', 'localhost']
    ips = ['127.0.0.1']
    
    if local_ip:
        ips.append(local_ip)
        print(f"📡 Detected local IP: {local_ip}")
    
    success, cert_file, key_file = generate_mkcert_certificate(hostnames, ips)
    if success and cert_file and key_file:
        CERT_FILE = cert_file
        KEY_FILE = key_file
        return True
    
    # Fall back to self-signed certificate generation
    if not check_mkcert_installed():
        print("\n⚠️  mkcert not found. Install it for trusted certificates:")
        print("   Windows: choco install mkcert")
        print("   Or download: https://github.com/FiloSottile/mkcert/releases")
        print("   Then run: mkcert -install")
        print("   Then: mkcert anton.local localhost 127.0.0.1 <your-ip>\n")
    
    print("🔐 Generating self-signed certificate (will show as untrusted)...")
    
    # Try cryptography library first (more reliable)
    if generate_cert_with_cryptography(hostnames, ips):
        print(f"✅ Generated self-signed certificate using cryptography library")
        print(f"   Certificate includes: {', '.join(hostnames)}, {', '.join(ips)}")
        print("   ⚠️  This certificate will show as 'Not secure' in browsers")
        print("   💡 Install mkcert for trusted certificates")
        return True
    
    # Fall back to OpenSSL
    print("⚠️  cryptography library not found, trying OpenSSL...")
    if generate_cert_with_openssl(hostnames, ips):
        print(f"✅ Generated self-signed certificate using OpenSSL")
        print(f"   Certificate includes: {', '.join(hostnames)}, {', '.join(ips)}")
        print("   ⚠️  This certificate will show as 'Not secure' in browsers")
        print("   💡 Install mkcert for trusted certificates")
        return True
    
    print("❌ Failed to generate certificate!")
    print("\nPlease install one of the following:")
    print("  1. mkcert (recommended): choco install mkcert")
    print("  2. cryptography: pip install cryptography")
    print("  3. OpenSSL: https://slproweb.com/products/Win32OpenSSL.html")
    return False

def main():
    """Start the HTTPS server."""
    global CERT_FILE, KEY_FILE
    
    # Change to project root so static files (index.html, libs/, etc.) are served correctly
    os.chdir(_PROJECT_ROOT)
    
    # Generate or find certificate
    if not generate_self_signed_cert():
        return
    
    # Verify certificate files exist
    if not (os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE)):
        print(f"❌ Certificate files not found: {CERT_FILE}, {KEY_FILE}")
        return
    
    # Check if using mkcert certificate
    is_mkcert = 'anton.local' in CERT_FILE and '+' in CERT_FILE
    
    # Create server
    try:
        with socketserver.TCPServer((HOST, PORT), MyHTTPRequestHandler) as httpd:
            # Wrap socket with SSL
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(CERT_FILE, KEY_FILE)
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            
            local_ip = get_local_ip()
            print("\n" + "="*60)
            print("🚀 HTTPS Server running!")
            print("="*60)
            if is_mkcert:
                print("✅ Using mkcert certificate (trusted by browsers)")
            else:
                print("⚠️  Using self-signed certificate (will show as 'Not secure')")
            print("="*60)
            print(f"📱 Local access:     https://localhost:{PORT}")
            print(f"📱 Hostname access:  https://anton.local:{PORT}")
            if local_ip:
                print(f"📱 IP access:        https://{local_ip}:{PORT}")
            print("="*60)
            if not is_mkcert:
                print("\n💡 To get a trusted certificate:")
                print("   1. Install mkcert: choco install mkcert")
                print("   2. Install CA: mkcert -install")
                print("   3. Generate cert: mkcert anton.local localhost 127.0.0.1 <your-ip>")
                print("   4. Restart this server")
            print("\n⚠️  iOS Safari Setup:")
            print("   1. Access the site from your iOS device")
            if is_mkcert:
                print("   2. Certificate should be trusted automatically")
                print("   3. If not, go to: Settings > General > About > Certificate Trust Settings")
            else:
                print("   2. Accept the security warning")
                print("   3. Go to: Settings > General > About > Certificate Trust Settings")
            print("   4. Enable 'Full Trust for Root Certificates' for this certificate")
            print("\n🛑 Press Ctrl+C to stop the server")
            print("="*60 + "\n")
            
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
    except OSError as e:
        if e.errno == 10048:  # Windows: Address already in use
            print(f"❌ Port {PORT} is already in use!")
            print(f"   Another server may be running on this port.")
        else:
            print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == '__main__':
    main()
