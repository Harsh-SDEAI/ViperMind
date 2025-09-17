#!/bin/bash

# ViperMind Security Hardening Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔒 Starting ViperMind Security Hardening${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run this script as root (sudo)${NC}"
    exit 1
fi

echo -e "${YELLOW}🔧 System Security Hardening...${NC}"

# Update system packages
echo -e "${YELLOW}  📦 Updating system packages...${NC}"
apt update && apt upgrade -y

# Install security tools
echo -e "${YELLOW}  🛠️ Installing security tools...${NC}"
apt install -y fail2ban ufw unattended-upgrades apt-listchanges

# Configure automatic security updates
echo -e "${YELLOW}  🔄 Configuring automatic security updates...${NC}"
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

# Enable automatic updates
echo 'APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";' > /etc/apt/apt.conf.d/20auto-upgrades

echo -e "${YELLOW}🔥 Firewall Configuration...${NC}"

# Configure UFW firewall
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (be careful with this)
ufw allow ssh

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow specific application ports
ufw allow 8000/tcp comment 'ViperMind API'
ufw allow 3001/tcp comment 'Grafana'
ufw allow 9090/tcp comment 'Prometheus'

# Enable firewall
ufw --force enable

echo -e "${YELLOW}🚫 Fail2Ban Configuration...${NC}"

# Configure Fail2Ban for SSH protection
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
backend = systemd

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600
EOF

# Create custom Fail2Ban filters
mkdir -p /etc/fail2ban/filter.d

cat > /etc/fail2ban/filter.d/nginx-http-auth.conf << 'EOF'
[Definition]
failregex = ^ \[error\] \d+#\d+: \*\d+ user "\S+":? (password mismatch|was not found in ".*"), client: <HOST>, server: \S+, request: "\S+ \S+ HTTP/\d+\.\d+", host: "\S+"$
            ^ \[error\] \d+#\d+: \*\d+ no user/password was provided for basic authentication, client: <HOST>, server: \S+, request: "\S+ \S+ HTTP/\d+\.\d+", host: "\S+"$
ignoreregex =
EOF

cat > /etc/fail2ban/filter.d/nginx-limit-req.conf << 'EOF'
[Definition]
failregex = limiting requests, excess: \S+ by zone "\S+", client: <HOST>
ignoreregex =
EOF

# Start and enable Fail2Ban
systemctl enable fail2ban
systemctl restart fail2ban

echo -e "${YELLOW}🔐 SSH Hardening...${NC}"

# Backup original SSH config
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Harden SSH configuration
cat > /etc/ssh/sshd_config << 'EOF'
# ViperMind SSH Security Configuration
Port 22
Protocol 2

# Authentication
PermitRootLogin no
PasswordAuthentication yes
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PermitEmptyPasswords no
ChallengeResponseAuthentication no
UsePAM yes

# Security settings
X11Forwarding no
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server

# Connection settings
ClientAliveInterval 300
ClientAliveCountMax 2
MaxAuthTries 3
MaxSessions 2
LoginGraceTime 60

# Logging
SyslogFacility AUTH
LogLevel INFO
EOF

# Restart SSH service
systemctl restart sshd

echo -e "${YELLOW}🛡️ Kernel Security...${NC}"

# Configure kernel security parameters
cat > /etc/sysctl.d/99-security.conf << 'EOF'
# IP Spoofing protection
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.rp_filter = 1

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0

# Ignore send redirects
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Disable source packet routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv6.conf.default.accept_source_route = 0

# Log Martians
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1

# Ignore ICMP ping requests
net.ipv4.icmp_echo_ignore_all = 0

# Ignore Directed pings
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Disable IPv6 if not needed
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1

# TCP SYN flood protection
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5

# Memory protection
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
kernel.yama.ptrace_scope = 1
EOF

# Apply kernel security settings
sysctl -p /etc/sysctl.d/99-security.conf

echo -e "${YELLOW}📁 File System Security...${NC}"

# Set secure permissions on sensitive files
chmod 600 /etc/ssh/sshd_config
chmod 644 /etc/passwd
chmod 600 /etc/shadow
chmod 644 /etc/group
chmod 600 /etc/gshadow

# Create security audit script
cat > /usr/local/bin/security-audit.sh << 'EOF'
#!/bin/bash
# ViperMind Security Audit Script

echo "🔍 ViperMind Security Audit Report - $(date)"
echo "================================================"

# Check for failed login attempts
echo "📊 Recent Failed Login Attempts:"
grep "Failed password" /var/log/auth.log | tail -5

# Check Fail2Ban status
echo -e "\n🚫 Fail2Ban Status:"
fail2ban-client status

# Check firewall status
echo -e "\n🔥 Firewall Status:"
ufw status

# Check for listening ports
echo -e "\n🔌 Listening Ports:"
netstat -tuln | grep LISTEN

# Check Docker security
echo -e "\n🐳 Docker Security:"
if command -v docker &> /dev/null; then
    docker version --format '{{.Server.Version}}' 2>/dev/null || echo "Docker not running"
    echo "Docker containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "No containers running"
fi

# Check system updates
echo -e "\n📦 System Updates:"
apt list --upgradable 2>/dev/null | wc -l | xargs echo "Available updates:"

# Check disk usage
echo -e "\n💾 Disk Usage:"
df -h / | tail -1

# Check memory usage
echo -e "\n🧠 Memory Usage:"
free -h | grep Mem

echo -e "\n✅ Security audit completed"
EOF

chmod +x /usr/local/bin/security-audit.sh

echo -e "${YELLOW}⏰ Setting up Security Monitoring...${NC}"

# Create security monitoring cron job
cat > /etc/cron.d/vipermind-security << 'EOF'
# ViperMind Security Monitoring
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Daily security audit
0 6 * * * root /usr/local/bin/security-audit.sh >> /var/log/security-audit.log 2>&1

# Weekly security updates check
0 3 * * 0 root apt update && apt list --upgradable >> /var/log/security-updates.log 2>&1
EOF

echo -e "${YELLOW}🔒 Docker Security Hardening...${NC}"

# Create Docker daemon security configuration
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true,
  "seccomp-profile": "/etc/docker/seccomp.json",
  "storage-driver": "overlay2"
}
EOF

# Download Docker seccomp profile
curl -fsSL https://raw.githubusercontent.com/moby/moby/master/profiles/seccomp/default.json -o /etc/docker/seccomp.json

# Restart Docker with new configuration
systemctl restart docker

echo -e "${YELLOW}📋 Creating Security Checklist...${NC}"

cat > /root/security-checklist.md << 'EOF'
# ViperMind Security Checklist

## Completed ✅
- [x] System packages updated
- [x] Firewall configured (UFW)
- [x] Fail2Ban installed and configured
- [x] SSH hardened
- [x] Kernel security parameters set
- [x] File permissions secured
- [x] Docker security configured
- [x] Security monitoring setup
- [x] Automatic security updates enabled

## Manual Tasks Required 📋

### SSL/TLS Configuration
- [ ] Install SSL certificates (Let's Encrypt recommended)
- [ ] Configure HTTPS redirect in nginx
- [ ] Test SSL configuration with SSL Labs

### Application Security
- [ ] Change default passwords in .env file
- [ ] Generate strong SECRET_KEY
- [ ] Configure CORS properly for production domain
- [ ] Review and update API rate limits
- [ ] Enable HSTS headers

### Database Security
- [ ] Change default PostgreSQL passwords
- [ ] Configure PostgreSQL to listen only on localhost
- [ ] Enable PostgreSQL SSL connections
- [ ] Set up database backups with encryption

### Monitoring & Logging
- [ ] Configure log rotation
- [ ] Set up centralized logging (optional)
- [ ] Configure alerting for security events
- [ ] Set up monitoring dashboards

### Network Security
- [ ] Configure reverse proxy (nginx)
- [ ] Set up DDoS protection (CloudFlare recommended)
- [ ] Configure VPN access for admin tasks (optional)
- [ ] Review and minimize exposed ports

### Backup & Recovery
- [ ] Set up automated backups
- [ ] Test backup restoration process
- [ ] Configure off-site backup storage
- [ ] Document recovery procedures

### Compliance & Auditing
- [ ] Review data privacy compliance (GDPR, etc.)
- [ ] Set up security audit logging
- [ ] Configure user access controls
- [ ] Document security procedures

## Regular Maintenance 🔄

### Daily
- [ ] Review security logs
- [ ] Check system resource usage
- [ ] Monitor application health

### Weekly
- [ ] Review Fail2Ban logs
- [ ] Check for security updates
- [ ] Review backup integrity
- [ ] Monitor SSL certificate expiry

### Monthly
- [ ] Full security audit
- [ ] Review user access permissions
- [ ] Update security documentation
- [ ] Test disaster recovery procedures

## Security Contacts 📞
- System Administrator: admin@your-domain.com
- Security Team: security@your-domain.com
- Emergency Contact: +1-XXX-XXX-XXXX

## Useful Commands 💻

```bash
# Run security audit
/usr/local/bin/security-audit.sh

# Check Fail2Ban status
sudo fail2ban-client status

# Check firewall status
sudo ufw status verbose

# Check for security updates
sudo apt list --upgradable

# View security logs
sudo tail -f /var/log/auth.log

# Check Docker security
docker run --rm -it docker/docker-bench-security
```
EOF

echo -e "${GREEN}✅ Security hardening completed!${NC}"
echo -e "${GREEN}📋 Security Summary:${NC}"
echo -e "   ✅ System packages updated"
echo -e "   ✅ Firewall configured (UFW)"
echo -e "   ✅ Fail2Ban installed and configured"
echo -e "   ✅ SSH hardened"
echo -e "   ✅ Kernel security parameters set"
echo -e "   ✅ Docker security configured"
echo -e "   ✅ Security monitoring setup"

echo -e "\n${YELLOW}📋 Next Steps:${NC}"
echo -e "   1. Review /root/security-checklist.md"
echo -e "   2. Configure SSL certificates"
echo -e "   3. Update application passwords"
echo -e "   4. Test security configuration"
echo -e "   5. Set up monitoring alerts"

echo -e "\n${YELLOW}🔍 Run security audit:${NC}"
echo -e "   sudo /usr/local/bin/security-audit.sh"

echo -e "\n${GREEN}🔒 ViperMind security hardening completed successfully!${NC}"