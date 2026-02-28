# LabEx Backend (Django)

این پروژه یک هسته‌ی بک‌اند برای پلتفرم Hands-on Lab است که:

- دوره/ماژول/لب/تسک را مدیریت می‌کند.
- برای هر کاربر سشن ایزوله‌ی آزمایشگاه ایجاد می‌کند.
- برای حل مرحله‌ها، اعتبارسنجی (Validation) انجام می‌دهد.
- مسیرهای جدا برای کاربر و ادمین دارد.

> در این نسخه عمداً Kubernetes، Message Queue و Billing حذف شده‌اند تا MVP سبک و قابل توسعه بسازیم.

---

## معماری ماژول‌ها

### `accounts`
- مدیریت User سفارشی بر پایه ایمیل.
- ثبت‌نام و ورود JWT.
- فایل‌های مهم:
  - `accounts/models.py`: مدل `User` و `UserManager`.
  - `accounts/serializers.py`: `RegisterSerializer` و `LoginSerializer`.
  - `accounts/api_client/auth.py`: endpointهای register/login.
  - `accounts/api_client/urls.py`: مسیرهای auth client.

### `courses`
- مدیریت دوره و ماژول.
- انتشار محتوا با status: `draft/published/archived`.
- فایل‌های مهم:
  - `courses/models.py`: `Course`, `CourseModule`, `PublishStatus`.
  - `courses/serializers.py`: serializerهای course/module.
  - `courses/views.py`: API عمومی فقط برای محتواهای `published`.
  - `courses/api_admin/course.py`: API ادمین برای CRUD کامل.
  - `courses/urls.py`: ترکیب routeهای عمومی و admin.

### `labs`
- هسته اصلی lab runtime و workflow.
- فایل‌های مهم:
  - `labs/models.py`
    - `Lab`: تنظیمات لب (image, difficulty, status)
    - `LabSection`: بخش‌های نظری/تسکی/راه‌حل
    - `LabTask`: مرحله‌های قابل اعتبارسنجی
    - `TaskValidationRule`: قانون تست برای هر تسک
    - `LabSession`: سشن اجرا برای هر کاربر
    - `TaskAttempt`: تاریخچه تلاش اعتبارسنجی
  - `labs/serializers.py`: serializer های lab/session/task.
  - `labs/views.py`: API عمومی + start/stop/detail session + validate task.
  - `labs/api_admin/labs.py`: CRUD ادمین برای lab/task/rule.
  - `labs/services/container_runtime.py`: اجرای امن کانتینر code-server با Docker.
  - `labs/services/grader.py`: اجرای ruleها داخل کانتینر (docker exec).
  - `labs/management/commands/cleanup_expired_sessions.py`: پاکسازی سشن‌های منقضی.

### `progress`
- ثبت پیشرفت در سطح Course/Lab/Task.
- فایل‌های مهم:
  - `progress/models.py`: `UserCourseProgress`, `UserLabProgress`, `UserTaskProgress`.

### `common`
- ابزارهای مشترک.
- فایل مهم:
  - `common/permissions.py`: مجوز `IsAdminOrInstructor`.

### `labex`
- تنظیمات مرکزی.
- فایل‌های مهم:
  - `labex/settings.py`: appها، DRF، JWT.
  - `labex/urls.py`: route ریشه + swagger/redoc.

---

## API ها

## احراز هویت
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`

نمونه Register:
```json
{
  "email": "user@example.com",
  "password": "StrongPass123",
  "password2": "StrongPass123"
}
```

## عمومی (Student)
- Courses:
  - `GET /api/courses/`
  - `GET /api/courses/{id}/`
- Modules:
  - `GET /api/modules/`
- Labs:
  - `GET /api/labs/`
  - `GET /api/lab-sections/`
  - `GET /api/lab-tasks/`
- Session:
  - `POST /api/labs/{lab_id}/start/`
  - `GET /api/sessions/{session_id}/`
  - `POST /api/sessions/{session_id}/stop/`
- Validation:
  - `POST /api/sessions/{session_id}/tasks/{task_id}/validate/`

## ادمین/مدرس
- Courses:
  - `GET/POST /api/admin/courses/`
  - `PUT/PATCH/DELETE /api/admin/courses/{id}/`
- Modules:
  - `GET/POST /api/admin/modules/`
- Labs:
  - `GET/POST /api/admin/labs/`
  - `GET/POST /api/admin/lab-sections/`
  - `GET/POST /api/admin/lab-tasks/`
  - `GET/POST /api/admin/validation-rules/`

---

## جریان حل لب
1. دانشجو `start lab` می‌زند.
2. سرویس runtime یک کانتینر code-server با محدودیت امنیتی می‌سازد.
3. اولین Task برای کاربر unlock می‌شود.
4. دانشجو روی `validate` می‌زند.
5. grader ruleها را با `docker exec` اجرا می‌کند.
6. اگر پاس شد:
   - attempt ذخیره می‌شود.
   - تسک بعدی unlock می‌شود.

---

## امنیت اجرا
در runtime سعی شده hardening اولیه اعمال شود:
- non-root user (`1000:1000`)
- `--read-only`
- `--cap-drop ALL`
- `--security-opt no-new-privileges`
- CPU/RAM/PID محدود

> نکته: برای production باید network policy، rootless docker/containerd و sandbox قوی‌تر اضافه شود.

---

## راه‌اندازی محلی

### 1) نصب وابستگی
```bash
pip install -r requirments.txt
```

### 2) Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3) اجرای سرور
```bash
python manage.py runserver
```

### 4) تست‌ها
```bash
pytest
```

### 5) پاکسازی session منقضی
```bash
python manage.py cleanup_expired_sessions
```

برای اجرای دوره‌ای cleanup می‌توانی cron تعریف کنی.

---

## نکات توسعه
- در MVP اگر Docker daemon در دسترس نباشد، `start_lab` با 503 برمی‌گردد.
- برای تست unit از `mock` روی runtime/grader استفاده شده تا وابسته به docker نباشد.
- پاسخ validator sanitize می‌شود تا جزئیات حساس فاش نشود.

---

## Docker Image Templates (`docker_images/`)

`Lab.docker_image` now stores an image key (template key), not a full Docker image ref.

Example keys:
- `python-dockerfile`
- `node-dockerfile`

The key is resolved through `LAB_DOCKER_IMAGE_MAP` in `labex/settings.py`:

```python
LAB_DOCKER_IMAGE_MAP = {
    "python-dockerfile": "ghcr.io/your-org/lab-python:1.0.0",
    "node-dockerfile": "ghcr.io/your-org/lab-node:1.0.0",
}
```

You can override this map with env var `LAB_DOCKER_IMAGE_MAP_JSON` (JSON object).

### Manual/CI build workflow

Build Python lab image:

```bash
docker build -t ghcr.io/your-org/lab-python:1.0.0 -f docker_images/python-dockerfile/Dockerfile .
```

Build Node lab image:

```bash
docker build -t ghcr.io/your-org/lab-node:1.0.0 -f docker_images/node-dockerfile/Dockerfile .
```

Push (example):

```bash
docker push ghcr.io/your-org/lab-python:1.0.0
docker push ghcr.io/your-org/lab-node:1.0.0
```

### Sync policy

- Every key in `LAB_DOCKER_IMAGE_MAP` must map to an existing built image tag.
- Keep keys stable (`python-dockerfile`) and bump image tags (`:1.0.1`) for updates.
- `start_lab` does not build images; it only resolves key -> image and runs the container.
