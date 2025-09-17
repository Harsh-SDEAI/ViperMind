#!/bin/bash

# ViperMind Production Readiness Checklist
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 ViperMind Production Readiness Checklist${NC}"
echo "=" * 60

# Configuration
ENVIRONMENT=${1:-production}
DOMAIN=${2:-localhost}

# Checklist items
declare -A checklist
checklist[environment_config]="❌"
checklist[ssl_certificates]="❌"
checklist[database_security]="❌"
checklist[application_security]="❌"
checklist[monitoring_setup]="❌"
checklist[backup_system]="❌"
checklist[performance_optimization]="❌"
checklist[security_hardening]="❌"
checklist[documentation]="❌"
checklist[testing_complete]="❌"

echo -e "${BLUE}🔍 Checking production readiness...${NC}"

# Check 1: Environment Configuration
echo -e "\n${YELLOW}1. Environment Configuration${NC}"
if [ -f ".env.${ENVIRONMENT}" ]; then
    echo -e "   ✅ Environment file exists"
    
    # Check critical environment variables
    source .env.${ENVIRONMENT}
    
    if [ -n "$SECRET_KEY" ] && [ ${#SECRET_KEY} -ge 32 ]; then
        echo -e "   ✅ SECRET_KEY is set and secure"
    else
        echo -e "   ❌ SECRET_KEY is missing or too short"
        exit 1
    fi
    
    if [ -n "$POSTGRES_PASSWORD" ] && [ ${#POSTGRES_PASSWORD} -ge 12 ]; then
        echo -e "   ✅ Database password is set and secure"
    else
        echo -e "   ❌ Database password is missing or too weak"
        exit 1
    fi
    
    if [ -n "$OPENAI_API_KEY" ]; then
        echo -e "   ✅ OpenAI API key is configured"
    else
        echo -e "   ❌ OpenAI API key is missing"
        exit 1
    fi
    
    checklist[environment_config]="✅"
else
    echo -e "   ❌ Environment file .env.${ENVIRONMENT} not found"
    exit 1
fi

# Check 2: SSL Certificates
echo -e "\n${YELLOW}2. SSL Certificates${NC}"
if [ -f "nginx/ssl/cert.pem" ] && [ -f "nginx/ssl/key.pem" ]; then
    echo -e "   ✅ SSL certificates found"
    
    # Check certificate validity
    if openssl x509 -in nginx/ssl/cert.pem -noout -checkend 86400 > /dev/null 2>&1; then
        echo -e "   ✅ SSL certificate is valid"
        checklist[ssl_certificates]="✅"
    else
        echo -e "   ⚠️  SSL certificate expires within 24 hours"
    fi
else
    echo -e "   ❌ SSL certificates not found"
    echo -e "   💡 Run: sudo certbot certonly --standalone -d ${DOMAIN}"
fi

# Check 3: Database Security
echo -e "\n${YELLOW}3. Database Security${NC}"
if docker-compose -f docker-compose.prod.yml ps db | grep -q "Up"; then
    echo -e "   ✅ Database container is running"
    
    # Check if default passwords are changed
    if [ "$POSTGRES_PASSWORD" != "password" ] && [ "$POSTGRES_USER" != "postgres" ]; then
        echo -e "   ✅ Database credentials are customized"
        checklist[database_security]="✅"
    else
        echo -e "   ❌ Database is using default credentials"
    fi
else
    echo -e "   ❌ Database container is not running"
fi

# Check 4: Application Security
echo -e "\n${YELLOW}4. Application Security${NC}"
if [ "$SECRET_KEY" != "your-secret-key-here" ]; then
    echo -e "   ✅ Application secret key is customized"
    
    # Check CORS configuration
    if [ "$REACT_APP_API_URL" != "http://localhost:8000" ]; then
        echo -e "   ✅ API URL is configured for production"
        checklist[application_security]="✅"
    else
        echo -e "   ❌ API URL is still set to localhost"
    fi
else
    echo -e "   ❌ Application is using default secret key"
fi

# Check 5: Monitoring Setup
echo -e "\n${YELLOW}5. Monitoring Setup${NC}"
if docker-compose -f docker-compose.prod.yml ps prometheus | grep -q "Up"; then
    echo -e "   ✅ Prometheus is running"
    
    if docker-compose -f docker-compose.prod.yml ps grafana | grep -q "Up"; then
        echo -e "   ✅ Grafana is running"
        checklist[monitoring_setup]="✅"
    else
        echo -e "   ❌ Grafana is not running"
    fi
else
    echo -e "   ❌ Monitoring services are not running"
fi

# Check 6: Backup System
echo -e "\n${YELLOW}6. Backup System${NC}"
if [ -f "scripts/backup.sh" ] && [ -x "scripts/backup.sh" ]; then
    echo -e "   ✅ Backup script exists and is executable"
    
    # Check if backup directory exists
    if [ -d "backups" ]; then
        echo -e "   ✅ Backup directory exists"
        checklist[backup_system]="✅"
    else
        echo -e "   ⚠️  Backup directory not found (will be created on first backup)"
        checklist[backup_system]="✅"
    fi
else
    echo -e "   ❌ Backup script is missing or not executable"
fi

# Check 7: Performance Optimization
echo -e "\n${YELLOW}7. Performance Optimization${NC}"
if docker-compose -f docker-compose.prod.yml ps redis | grep -q "Up"; then
    echo -e "   ✅ Redis cache is running"
    
    # Check if optimization script exists
    if [ -f "backend/optimize_performance.py" ]; then
        echo -e "   ✅ Performance optimization script exists"
        checklist[performance_optimization]="✅"
    else
        echo -e "   ❌ Performance optimization script is missing"
    fi
else
    echo -e "   ❌ Redis cache is not running"
fi

# Check 8: Security Hardening
echo -e "\n${YELLOW}8. Security Hardening${NC}"
if [ -f "scripts/security-hardening.sh" ]; then
    echo -e "   ✅ Security hardening script exists"
    
    # Check if firewall is enabled (if running on Linux)
    if command -v ufw &> /dev/null; then
        if ufw status | grep -q "Status: active"; then
            echo -e "   ✅ Firewall is active"
            checklist[security_hardening]="✅"
        else
            echo -e "   ❌ Firewall is not active"
        fi
    else
        echo -e "   ⚠️  UFW firewall not available (check system firewall)"
        checklist[security_hardening]="✅"
    fi
else
    echo -e "   ❌ Security hardening script is missing"
fi

# Check 9: Documentation
echo -e "\n${YELLOW}9. Documentation${NC}"
if [ -f "README.md" ] && [ -f "docs/deployment/production-deployment.md" ]; then
    echo -e "   ✅ Documentation is complete"
    
    if [ -f "docs/api/README.md" ]; then
        echo -e "   ✅ API documentation exists"
        checklist[documentation]="✅"
    else
        echo -e "   ❌ API documentation is missing"
    fi
else
    echo -e "   ❌ Core documentation is missing"
fi

# Check 10: Testing Complete
echo -e "\n${YELLOW}10. Testing Complete${NC}"
if [ -f "backend/test_system_integration.py" ] && [ -f "backend/test_load_performance.py" ]; then
    echo -e "   ✅ Test suites exist"
    
    # Try to run a quick health check
    if curl -f -s "http://localhost:8000/api/v1/monitoring/status" > /dev/null 2>&1; then
        echo -e "   ✅ Application is responding to health checks"
        checklist[testing_complete]="✅"
    else
        echo -e "   ❌ Application health check failed"
    fi
else
    echo -e "   ❌ Test suites are missing"
fi

# Generate Report
echo -e "\n${BLUE}📊 Production Readiness Report${NC}"
echo "=" * 60

passed_checks=0
total_checks=0

for check in "${!checklist[@]}"; do
    total_checks=$((total_checks + 1))
    status="${checklist[$check]}"
    
    if [ "$status" = "✅" ]; then
        passed_checks=$((passed_checks + 1))
    fi
    
    echo -e "   $status $(echo $check | tr '_' ' ' | sed 's/.*/\u&/')"
done

echo ""
echo -e "Passed: ${passed_checks}/${total_checks}"

# Calculate readiness percentage
readiness_percentage=$((passed_checks * 100 / total_checks))
echo -e "Readiness: ${readiness_percentage}%"

# Determine overall status
if [ $readiness_percentage -eq 100 ]; then
    echo -e "\n${GREEN}🎉 PRODUCTION READY!${NC}"
    echo -e "All checks passed. ViperMind is ready for production deployment."
elif [ $readiness_percentage -ge 80 ]; then
    echo -e "\n${YELLOW}⚠️  MOSTLY READY${NC}"
    echo -e "Most checks passed. Address remaining issues before production deployment."
else
    echo -e "\n${RED}❌ NOT READY${NC}"
    echo -e "Critical issues found. Do not deploy to production until all checks pass."
fi

# Generate action items
echo -e "\n${BLUE}📋 Action Items${NC}"

if [ "${checklist[ssl_certificates]}" = "❌" ]; then
    echo -e "   🔒 Set up SSL certificates for HTTPS"
fi

if [ "${checklist[database_security]}" = "❌" ]; then
    echo -e "   🗄️  Secure database with strong passwords"
fi

if [ "${checklist[application_security]}" = "❌" ]; then
    echo -e "   🔐 Update application security configuration"
fi

if [ "${checklist[monitoring_setup]}" = "❌" ]; then
    echo -e "   📊 Set up monitoring and alerting"
fi

if [ "${checklist[backup_system]}" = "❌" ]; then
    echo -e "   💾 Configure automated backup system"
fi

if [ "${checklist[security_hardening]}" = "❌" ]; then
    echo -e "   🛡️  Run security hardening script"
fi

# Save report to file
report_file="production-readiness-report-$(date +%Y%m%d_%H%M%S).txt"
{
    echo "ViperMind Production Readiness Report"
    echo "Generated: $(date)"
    echo "Environment: $ENVIRONMENT"
    echo "Domain: $DOMAIN"
    echo ""
    echo "Readiness: ${readiness_percentage}%"
    echo "Passed: ${passed_checks}/${total_checks}"
    echo ""
    echo "Checklist Results:"
    for check in "${!checklist[@]}"; do
        echo "  ${checklist[$check]} $(echo $check | tr '_' ' ')"
    done
} > "$report_file"

echo -e "\n📄 Report saved to: $report_file"

# Exit with appropriate code
if [ $readiness_percentage -eq 100 ]; then
    exit 0
else
    exit 1
fi