
# 🛠️ Project Status: Active Development (Backend-First Phase)
*Note: The core architecture is fucntional, but edge-case error handling and frontend client integration are currently being built in active sprints.*



# 🥬 Veggie Vault

Veggie Vault is an online grocery shopping store website (e-commerce webapp). 

---

## 📁 Project Folders

* **`/.venv`**: Local Python virtual environment containing isolated project dependencies (Django, Razorpay SDK, Celery, etc.). *Note: This folder is excluded from version control.*
* **`/Backend`**: The server-side code built with Django.
  * **`VeggieVault/`**: The main configuration folder for the project.
    * `__init__.py`: Tells Python that this is a project folder.
    * `settings.py`: The main settings file where database, apps, and tools like Razorpay are set up.
    * `urls.py`: The routing file that directs website links to the right features.
    * `celery.py`: Setting up background tasks (like checking system status every minute).
    * `asgi.py` & `wsgi.py`: Tools used to deploy and run the website on a server.
  * **`app_locations/`**: Logistics and geographical data management for consumer deliveries.
    * `migrations/`: Holds database migration files tracking structure updates for address records.
    * `__init__.py`: Tells Python that this is an importable folder.
    * `admin.py`: Registers location schemas within the Django Admin portal for logistical oversight.
    * `apps.py`: Application metadata configuration for initialization hooks.
    * `models.py`: Structural definitions for delivery destinations, enforcing strict alphanumeric character sanitation via custom `RegexValidator` guard rails.
    * `serializers.py`: Formats, maps, and validates incoming client address structures into structured location records.
    * `services.py`: Dedicated layer for address manipulation, verification logic, and user-profile assignment loops.
    * `tests.py`: Test suite verifying structural address sanitation and endpoint routing behaviors.
    * `views.py`: API endpoints for creating, updating, and querying user-saved destination locations.
  * **`app_orders/`**: Transactional engine managing checkout, order tracking, and payment flows.
    * `tests/`: Testing folder isolated with internal routing mock scripts (`test_urls.py`) to safely test order states.
    * `__init__.py`: Tells Python that this is an importable folder.
    * `admin.py`: Registers order manifests and financial payment rows within the Admin portal.
    * `apps.py`: Application metadata configuration for initialization hooks.
    * `models.py`: Database tables defining customer orders, protected line-item summaries (`on_delete=models.PROTECT`), and multi-state tracking for Razorpay signatures and payments.
    * `serializers.py`: Manages explicit primary key deserialization alongside safe relational layouts (`ProductNestedSerializer`), and enforces strict regex filtering on gateway validation tokens.
    * `services.py`: Implements `OrderCreationService` to handle currency parsing for Razorpay (converting INR to Paise) and atomic multi-model status syncing (`transaction.atomic`) for payment state transitions (`captured` vs `failed`).
    * `urls.py`: Exposes routing paths for fetching comprehensive historical line-items, triggering new remote payment orders, and executing cryptographic signature verifications.
    * `utils.py`: Data transformation utilities handling cross-app model translations, converting live `Cart` structures to checkout line items, and handling full cart restoration schemas for payment failures.
    * `views.py`: API processors routing orders through structured status updates. Includes transactional safe checkout views, cryptographic signature verification processors, and an `AllowAny` webhook entry point to sync server-side states with asynchronous gateway push events.
  * **`app_products/`**: Inventory management and shopping cart subsystem.
    * `tests/`: Testing directory verifying endpoint, model, view, and serializer behaviors securely.
    * `__init__.py`: Tells Python that this is an importable folder.
    * `admin.py`: Registers product entities with the Django Admin portal for backend oversight.
    * `apps.py`: Application metadata configuration for initialization hooks.
    * `models.py`: Structural definitions for products (handling collision-free auto-slug generation) and Cart intermediary instances.
    * `serializers.py`: Transforms core product schemas and parses dynamic runtime calculations like item pricing totals.
    * `services.py`: Cart transactional logic layer that safely intercepts structural modifications inside data-safe wrapper blocks.
    * `urls.py`: Exposes routing paths for product catalogues, individual slugs, and relational cart objects.
    * `views.py`: API handlers managing advanced query search filtering engine properties (`DjangoFilterBackend`) and cart updates.
  * **`app_users/`**: Core user management app handling authentication, profiles, and permissions.
    * `tests/`: Testing directory verifying endpoint, model, view, and serializer behaviors securely.
    * `__init__.py`: Tells Python that this is an importable folder.
    * `admin.py`: Registers user schemas with the Django Admin portal for backend oversight.
    * `apps.py`: Application metadata configuration for initialization hooks.
    * `models.py`: Defines separate tables for credential core users, profile records, and 10-minute email verification limits.
    * `serializers.py`: Sanitizes incoming login data, protects sensitive passwords using write-only barriers, and parses location array structures.
    * `services.py`: The business processing engine executing password alterations, atomic address mutation loops, and asynchronous email worker trigger delays.
    * `urls.py`: Maps endpoint paths for account management, authentication flows, password recovery, and nested location arrays.
    * `views.py`: Robust API controllers executing account actions backed up with Sentry crash interceptors and safe HttpOnly JWT cookies.
  * **`base/`**: Core app containing shared utilities, base models, and background tasks used by all other apps.
    * `__init__.py`: Tells Python that this is an importable folder.
    * `exceptions.py`: Custom error types (like NotFound or AuthenticationError) to handle failures uniformly.
    * `helpers.py`: Utility functions, including strict type-casting helpers for API data validation.
    * `models.py`: Abstract foundation model tracking UUID keys and created/updated timestamps for database tables.
    * `services.py`: Dedicated system engine features, such as building and routing transactional emails.
    * `tasks.py`: Asynchronous workers managed by Celery to process heavy operational flows (like email delivery) in the background.
  * **`config/settings/`**: Environment-specific settings overrides that scale the app for dev, test, or production.
    * `__init__.py`: Tells Python that this is an importable folder.
    * `settings_dev.py`: Configuration file for local development that turns on active development JSON logging.
    * `settings_prod.py`: Production-safe settings that disable debug tracking and connect live application monitoring to **GlitchTip**.
    * `settings_test.py`: Isolated settings for test execution that initialize an ultra-fast in-memory SQLite database, mock background tasks, and pipe test logs to the screen.
  * **`logging_confgs/`**: Custom configuration setup for tracking system logs and recording errors.
    * `__init__.py`: Tells Python that this is an importable folder.
    * `logging_config.json`: The rulebook file that decides which errors to catch, how to format them (text or JSON), and limits log file sizes to 3MB.
    * `log_cnfgs_setter.py`: The control script that configures where logs are saved and optimizes performance between normal development mode and testing mode.
    * `jsonlogger.py`: A custom tool that rewrites standard text logs into organized JSON objects, automatically injects UTC/IST timestamps, and separates normal info logs from system errors.
  * **`logs/`**: The storage folder where active log files are written.
    * `django_errors.log.jsonl`: The active log file tracking warnings and errors during development.
    * `django_test_errors.log.jsonl`: The dedicated log file used to capture issues while running test suites.
  * **`media/`**: Stores uploaded files and photos for the website.
    * **`images/products/`**: Holds images of the grocery items (like tomatoes, apples, etc.).
    * **`images/users/`**: Holds user profile pictures.
  * **`testing_data/`**: Folder containing helper scripts to set up the app for testing.
    * `fill_dummy_data.py`: A script that automatically fills your database with test items, users, and orders.
  * **`manage.py`**: A command file used to run the project. It is customized to load your secret settings automatically from a `.env` file.
* **`/Frontend`**: Empty for now. We will build the user interface screen here later.

## 📁 Project Folders Tree Structure

```text
Backend/                <- Project Root Directory
├── .env                <- Local environment secrets and credentials (Excluded from VCS)
├── .venv/              <- Isolated Python virtual environment (Excluded from VCS)
├── manage.py           <- Custom environment-loading initialization script
├── requirements.txt    <- Complete Python package dependencies manifest
├── VeggieVault/        <- Core Project Configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   ├── asgi.py
│   └── wsgi.py
├── app_locations/      <- Delivery Destinations & Logistics Management
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests.py
│   └── views.py
├── app_orders/         <- Checkout, Payments & State Engine
│   ├── tests/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── app_products/       <- Inventory Control & Dynamic Shopping Carts
│   ├── tests/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── urls.py
│   └── views.py
├── app_users/          <- Authentication & Profile Authorization
│   ├── tests/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── urls.py
│   └── views.py
├── base/               <- Shared Utilities & Global Core Layer
│   ├── __init__.py
│   ├── exceptions.py
│   ├── helpers.py
│   ├── models.py
│   ├── services.py
│   └── tasks.py
├── config/             <- Environment Setting Overrides
│   └── settings/
│       ├── __init__.py
│       ├── settings_dev.py
│       ├── settings_prod.py
│       └── settings_test.py
├── logging_confgs/     <- Logging System Core Configuration
│   ├── __init__.py
│   ├── logging_config.json
│   ├── log_cnfgs_setter.py
│   └── jsonlogger.py
├── logs/               <- Storage Area for Live Log Writing
│   ├── django_errors.log.jsonl
│   └── django_test_errors.log.jsonl
├── media/              <- Dynamic User Upload Directories
│   └── images/
│       ├── products/
│       └── users/
└── testing_data/       <- Core Testing Data Generation Tools
    └── fill_dummy_data.py
---
```

## 🛠️ How the Backend is Built

Here is a simple look at what tools and features are inside the project right now:

### 🧩 Website Features (Django Apps)
* `app_users`: Handles user accounts, custom logins, and profiles (Consumers, Workers, Admins).
* `app_products`: Manages the grocery items (Vegetables & Fruits), categories, prices, and stock.
* `app_locations`: Manages delivery addresses and geographical data.
* `app_orders`: Tracks the shopping cart, customer checkout, and order status.
* `base`: Holds general tools and helper tasks for the system.

### 🔌 Connected Tools & Integrations
* **Database:** Uses **MySQL** to save data (and has drivers ready for **PostgreSQL** too).
* **Login Security:** Uses secure JWT tokens to keep users logged in safely.
* **Payments:** Set up with **Razorpay** to handle customer payments.
* **Emails:** Connected to **Gmail** to send automated emails to users.
* **Background Tasks:** Uses **Celery** and **Redis** to do heavy tasks in the background without slowing down the website.

---

## ⚙️ Initial Setup & Local Installation

Execute these commands from your repository terminal space to spin up the backend server locally. First, navigate into your backend directory:

```bash
cd Backend
```

### 1. Activate the Virtual Environment
```bash
# On Windows (Command Prompt)
.venv\Scripts\activate

# On Windows (PowerShell)
.venv\Scripts\Activate.ps1

# On macOS/Linux
source .venv/bin/activate
```

### 2. Install Project Requirements
Make sure your dependencies stay up to date:

```Bash
pip install -r requirements.txt
```

### 3. Run Database Migrations
```Bash
python manage.py makemigrations
python manage.py migrate
```
--------------------------------------------------------------------------------
🔑 ENVIRONMENT CONFIGURATION (.env)
--------------------------------------------------------------------------------
This project requires several environment variables to function correctly. 
Follow these steps to set up your `.env` file in the `Backend/` directory:

1. Create a new file named `.env` in the `Backend/` folder.
2. Copy the template below and fill in the values as described.

## --- .env TEMPLATE ---

### 1. Environment Settings
#### Set DJANGO_ENV to 'test', 'dev', or 'prod' depending on your usage
DJANGO_ENV=test
DJANGO_SETTINGS_MODULE=config.settings.settings_test
DEBUG=True
#### Generate a random string for your secret key
DJANGO_SECRET_KEY=your_long_random_string_here
#### DSN provided by your GlitchTip project settings
GLITCHTIP_DSN=

### 2. Email Configuration
#### Use your Gmail address and an "App Password" (NOT your regular login password)
#### Generate App Password here: https://myaccount.google.com/apppasswords
USER_EMAIL=your_name@gmail.com
USER_EMAIL_PASSWORD=your_app_password_here

### 3. Task Queue
#### Ensure Redis is installed and running locally
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_TASK_ALWAYS_EAGER=False
CELERY_TASK_EAGER_PROPAGATES=True

### 4. Payment Gateway (Razorpay)
#### Get these keys from your Razorpay Dashboard (Settings > API Keys)
RAZORPAY_TEST_API_KEY=rzp_test_xxxxxx
RAZORPAY_TEST_KEY_SECRET=your_secret_key_here

--------------------------------------------------------------------------------
⚙️ SETTINGS MANAGEMENT
--------------------------------------------------------------------------------
This project uses separate Django settings files for different environments.
You can control which one is active via the `DJANGO_SETTINGS_MODULE` variable 
in your `.env` file.

* **Development:** Use `config.settings.settings_dev`
  (Ideal for local coding, enables debug mode, local database)

* **Testing:** Use `config.settings.settings_test`
  (Used for running unit tests, uses ephemeral or test databases)

* **Production:** Use `config.settings.settings_prod`
  (Highly secure, handles static files, production database settings)

To switch, simply update the line in your `.env` file:
DJANGO_SETTINGS_MODULE=config.settings.settings_dev

## 🧪 Running the Test Suite

To run tests, you must specify the path using a **dot-notation structure** (`App.Module.File.Class.Method`). 

### The Syntax:
```bash
python manage.py test <App_Name>.<Folder_name>.<Test_File>.<Test_ClassName>.<TestFunctionName> --debug-mode
```
### Practical Example
If you want to run one specific test case in your order operations, use the following:

```bash
python manage.py test app_orders.tests.test_cases.OrderOperationsTest.test_razorpay_verify_payment --debug-mode
```

```bash
python manage.py test <App_Name>.<Folder_name>.<Test File>.<TestClassName>.<TestFunctionName> --debug-mode
```
> **Note:** Ensure there are **no spaces** in the path. If you omit the specific method or class, Django will automatically run all tests within the specified scope (e.g., all tests in a file or all tests in an app).

* **Example:**
```bash
python manage.py test app_orders.tests.test_cases.OrderOperationsTest.test_razorpay_verify_payment --debug-mode
```

## 🚀 Running the Services

Because **Veggie Vault** uses Celery for background tasks, you need **four** separate terminal windows to run the full stack:

| Terminal | Command | Purpose |
| :--- | :--- | :--- |
| **1. Django Server** | `python manage.py runserver` | Starts the main API gateway |
| **2. Celery Worker** | `#celery -A VeggieVault worker -l info --pool=solo` | Processes background emails/tasks |
| **3. Celery Beat** | `celery -A VeggieVault beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler` | Triggers scheduled tasks |
| **4. Redis (Required)** | `redis-server` | Message broker for Celery |

> **💡 Pro-Tip for Windows Users:** If you are running Celery on Windows, standard `fork` is not supported. Use this command for the worker instead:
> `celery -A VeggieVault worker --loglevel=info --pool=eventlet`


## 🧪 How to Insert Sample Test Data
I have included a setup script that automatically wipes out any old test data and fills your database with 10 sample addresses, 10 sample users/profiles, 10 grocery products (fruits and vegetables), and dummy order items. It also automatically sets up an Admin Account for you.

### Execute this command from the project root directory:
```bash
python testing_data/fill_dummy_data.py
```


### 🔑 Default Admin Login Created
Email: admin@example.com

Password: admin123

### 🛡️ Django Admin Portal
You can manage store data, inventory, and user records directly through the built-in Django Admin interface.

* **URL:** `http://127.0.0.1:8000/admin/`
* **Default Credentials:** Use the admin account created by the `fill_dummy_data.py` script:
  * **Email:** `admin@example.com`
  * **Password:** `admin24`
* **Create Your Own:** If you prefer to create your own administrative account, run the following command from the `Backend/` directory:
  ```bash
  python manage.py createsuperuser
  ```


## 🚀 Complete API Architecture & Routing

The master routing file `Backend/VeggieVault/urls.py` acts as the gatekeeper, prefixing all features under versioned API pathways (`''`). 
---

### 1. User Account (`app_users`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/user/create/` | Register new user |
| `POST` | `/user/check/` | Check user status |
| `POST` | `/login/` | User login |
| `POST` | `/forget-password/` | Initiate recovery |
| `POST` | `/change-password/` | Change password |
| `GET` | `/profiles/` | List all profiles |
| `GET` | `/profile/` | Manage own profile |
| `POST` | `/profile/location/update/` | Update address |
| `GET` | `/profile/locations/` | List addresses |
| `DELETE`| `/profile/locations/delete/` | Remove address |
| `POST` | `/profile/locations/create` | Add new address |

### 2. Products & Cart (`app_products`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/products/` | Catalog list |
| `GET` | `/product/<slug:slug>` | Product detail |
| `GET/POST` | `/profile/cart/` | List/Add to cart |
| `PUT/PATCH/DELETE` | `/profile/cart/<uuid:uid>/` | Modify cart items |

### 3. Orders & Payments (`app_orders`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/orders/` | View order history |
| `POST` | `/razorpay/order/create` | Initialize payment |
| `POST` | `/razorpay/order/payment/verify` | Verify transaction |

---

## 💡 Important Notes
* **JWT Auth:** Token operations are available at `/api/token/` and `/api/token/refresh/`.
* **Access:** Most `profile/` and `orders/` endpoints require a valid Bearer token in the request header.

---

### 🛠️ Core Request / Response Payloads (Examples)

#### User Creation (`POST /user/create/`)

* **Request (`application/json`):**
```json
{
          "email": "name@domain.com",      
          "password": "name1234"    
}
```

* **Responses :**
* * **Response 1:**
status 200 Created

```json
{
  "message": "New user created successfully"
}
```
* * **Response 2:**
status 500 Internal Server Error

```json
{
  "error": "server error occured"
}
```
---

## 📖 Live Interactive API Documentation

While the examples above highlight core operational workflows, the entire backend API schema is mapped dynamically using **OpenAPI 3.0**. 

Once you spin up the local development server, you can view, test, and interact with **every single endpoint** across all apps by navigating to:
[`http://127.0.0.1:8000/api/docs/`](http://127.0.0.1:8000/api/docs/)
* **Swagger UI:** [`http://127.0.0.1:8000/api/docs/`](http://127.0.0.1:8000/api/docs/)
* **ReDoc UI:** [`http://127.0.0.1:8000/api/redoc/`](http://127.0.0.1:8000/api/redoc/)