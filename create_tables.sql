USE PY_SHOPS;

-- Incoming Goods Table
CREATE TABLE incoming_goods (
    id INT PRIMARY KEY IDENTITY(1,1),
    delivery_note VARCHAR(50),
    sscc VARCHAR(50),
    sales_order VARCHAR(50),
    document_msi VARCHAR(50),
    item_code VARCHAR(50),
    description TEXT,
    uom VARCHAR(20),
    quantity DECIMAL(18,2),
    receiver VARCHAR(100),
    customer VARCHAR(100),
    delivery_type VARCHAR(50),
    order_type VARCHAR(50),
    created_at DATETIME DEFAULT GETDATE(),
    status VARCHAR(20) DEFAULT 'PENDING'
);

-- Users Table
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255),
    email VARCHAR(100),
    full_name VARCHAR(100),
    branch_id INT,
    role_id INT,
    is_active BIT DEFAULT 1,
    last_login DATETIME
);

-- Branches Table
CREATE TABLE branches (
    id INT PRIMARY KEY IDENTITY(1,1),
    branch_code VARCHAR(20) UNIQUE,
    branch_name VARCHAR(100),
    address TEXT,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100)
);

-- Roles Table
CREATE TABLE roles (
    id INT PRIMARY KEY IDENTITY(1,1),
    role_name VARCHAR(50),
    description TEXT
);

-- Permissions Table
CREATE TABLE permissions (
    id INT PRIMARY KEY IDENTITY(1,1),
    permission_name VARCHAR(50),
    description TEXT
);

-- Role Permissions Table
CREATE TABLE role_permissions (
    role_id INT,
    permission_id INT,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
);

-- Audit Logs Table
CREATE TABLE audit_logs (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT,
    action VARCHAR(50),
    table_name VARCHAR(50),
    record_id INT,
    old_value TEXT,
    new_value TEXT,
    timestamp DATETIME DEFAULT GETDATE(),
    ip_address VARCHAR(50)
);

-- Scanner Devices Table
CREATE TABLE devices (
    id INT PRIMARY KEY IDENTITY(1,1),
    device_id VARCHAR(100) UNIQUE,
    branch_id INT,
    last_sync DATETIME,
    status VARCHAR(20),
    registered_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (branch_id) REFERENCES branches(id)
);

-- Add foreign key constraints
ALTER TABLE users ADD CONSTRAINT FK_Users_Branches 
FOREIGN KEY (branch_id) REFERENCES branches(id);

ALTER TABLE users ADD CONSTRAINT FK_Users_Roles
FOREIGN KEY (role_id) REFERENCES roles(id);

-- Create indexes for better performance
CREATE INDEX IX_incoming_goods_sscc ON incoming_goods(sscc);
CREATE INDEX IX_incoming_goods_delivery_note ON incoming_goods(delivery_note);
CREATE INDEX IX_users_username ON users(username);
CREATE INDEX IX_branches_branch_code ON branches(branch_code);
