
# Red Shell Recruiting - Candidate Submission App

---

##  Tech Stack

- Python 3.10
- Django 4.x
- PostgreSQL
- AWS S3 (for resume storage)
- jQuery (frontend dynamic behavior)
- Docker + Docker Compose (for containerization)
- Terraform (for AWS infrastructure provisioning)
- Poetry (for dependency management)

---

##  Setup Instructions

### 1. Local Dev (Poetry)

#### Environment Variables

```bash
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=your-region
DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage
DEBUG=True
DJANGO_SECRET_KEY=your-local-dev-secret-key
```

#### Install Requirements

```bash
poetry install
```

---

##  Docker-Compose for Production

- The app runs internally on **port 5000**, mapped to external **port 5001** (configurable via `.env.prod`).
- **Nginx reverse proxy** runs on **port 80** and **port 443** for HTTPS traffic.
- **Certbot** container is included to handle SSL certificate generation and renewal.
- **Environment variables** are loaded from `.env.prod`.
- Application is launched via `/docker-entrypoint.sh`.
- Network: `red-shell-recruiting_red-shell-recruiting`.

#### To run in production:

```bash
docker-compose -f docker-compose.prod.yml --profile production up -d
```

---

##  EC2 Instance Bootstrap Script (`web_app_startup.sh`)

- Installs Docker and Docker-Compose if not already installed.
- Starts Docker service and ensures `ec2-user` has Docker permissions.
- Navigates to project directory `/home/ec2-user/red-shell-recruiting`.
- Launches the app using:

```bash
docker-compose -f docker-compose.prod.yml --profile production up -d
```

This bootstraps a clean EC2 instance to full production deployment.

---


##  HTTPS with Certbot

- The `certbot` container handles SSL certificate generation and renewal.
- Nginx container uses mounted Let's Encrypt certificates to serve HTTPS traffic.
- **Initial certificate request** (first time only) must be done manually using:

```bash
docker-compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email darren.rooney101587@outlook.com \
  --agree-tos \
  --no-eff-email \
  -d redshellrecruiting.com \
  -d www.redshellrecruiting.com
```

This command tells Certbot to:
- Use **webroot** method to verify ownership.
- Use `/var/www/certbot` as the verification directory (served by nginx).
- Obtain certificates for both the apex domain and www subdomain.
- Register your admin email without subscribing to EFF mailing list.

After the certs are issued, nginx will automatically pick them up (mounted volumes).

---

###  Auto-renewal Tip

To automatically renew the certificates, you can create a cron job or periodic task inside the server that runs:

```bash
docker-compose run --rm certbot renew
```

This checks if the certificates are nearing expiration and renews them if needed.

You can test automatic renewal with:

```bash
docker-compose run --rm certbot renew --dry-run
```

Let's Encrypt recommends renewing at least once every 60 days.

---

#  Quick Paths

Once issued, certificates are stored at:

```bash
/etc/letsencrypt/live/redshellrecruiting.com/fullchain.pem
/etc/letsencrypt/live/redshellrecruiting.com/privkey.pem
```

These paths are mounted into the nginx container via `docker-compose.prod.yml`.


---

##  Terraform Infrastructure

- `main.tf`, `variables.tf`, `terraform.tfvars` define AWS resources:
    - VPC
    - EC2 Instance
    - Security Groups
    - (Optional) RDS PostgreSQL Database (`rds.tf`)
- Parameters like instance type, region, database size, etc. are managed in `terraform.tfvars`.

Full Infrastructure as Code (IaC) setup for scalable deployments.

---

##  User Account Management

- Supports user **Signup**, **Login**, **Logout**, and **Password Change**.
- **Two-Factor Authentication (2FA)** supported via TOTP apps (e.g., Google Authenticator).
- **Backup Codes** available after enabling 2FA.
- Users can **disable 2FA** if needed.
- **All protected views require login** (`@login_required`).
- Resume uploads and candidate submissions are restricted to **authenticated users only**.

Secure access to the application is enforced.

---

##  Candidate Form Details

| Field | Required | Details |
|:---|:---|:---|
| First Name |  | Text input |
| Last Name |  | Text input |
| State |  | Dropdown selector |
| City |  | Dropdown populated after state |
| Job Title |  | Text input |
| Phone Number |  | Text input (auto-formats as `555-555-5555`) |
| Email |  | Text input (`type=email`) |
| Compensation |  | Numeric input |
| Notes |  | Large textarea |
| Resume Upload |  | File input (.pdf, .doc, .docx)

---

##  Validation

### Client-side (jQuery)

- Validates that State and City are selected
- Validates phone number structure (10-15 digits)
- Validates email format using regex
- Auto-formats phone number on typing

### Server-side (Django)

- `validate_email()` for email addresses
- Regex phone number check
- Enforces required fields and file upload

---

##  Resume Uploads

Stored structure:

```
resumes/{candidate_id}/{original_filename}_YYYY_MM_DD_HHMMSS.ext
```

Example:

```
resumes/123/darren_resume_2025_04_26_015230.docx
```

Prevents file overwrite and keeps uploads clean.

---

##  Models Overview

### CandidateProfile

```python
class CandidateProfile(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    compensation = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(null=True, blank=True)
    open_to_relocation = models.BooleanField(default=False)
    currently_working = models.BooleanField(default=True)
    actively_looking = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Resume

```python
class Resume(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to=resume_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

##  Dev Commands

| Task | Command |
|:---|:---|
| Run server locally | `poetry run python manage.py runserver` |
| Make migrations | `poetry run python manage.py makemigrations` |
| Apply migrations | `poetry run python manage.py migrate` |
| Create superuser | `poetry run python manage.py createsuperuser` |
| Run Docker local | `docker-compose up --build` |
| Run Docker production | `docker-compose -f docker-compose.prod.yml --profile production up -d` |

---

Ready for production-level candidate intake, AWS deployment, and resume management!
