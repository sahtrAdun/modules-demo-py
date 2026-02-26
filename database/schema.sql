CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT CHECK(role IN ('guest', 'client', 'manager', 'admin')) NOT NULL
);

CREATE TABLE Categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE Manufacturers (
    manufacturer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer_name TEXT NOT NULL UNIQUE
);

CREATE TABLE Suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name TEXT NOT NULL UNIQUE
);

CREATE TABLE Units (
    unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_name TEXT NOT NULL UNIQUE
);

CREATE TABLE PickupPoints (
    pickup_point_id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL UNIQUE
);

CREATE TABLE Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    article TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    description TEXT,
    manufacturer_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL CHECK(price >= 0),
    unit_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity >= 0),
    discount INTEGER DEFAULT 0 CHECK(discount >= 0 AND discount <= 100),
    image_path TEXT,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE RESTRICT,
    FOREIGN KEY (manufacturer_id) REFERENCES Manufacturers(manufacturer_id) ON DELETE RESTRICT,
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id) ON DELETE RESTRICT,
    FOREIGN KEY (unit_id) REFERENCES Units(unit_id) ON DELETE RESTRICT
);

CREATE TABLE Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_article TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('new', 'processing', 'completed', 'cancelled')) NOT NULL,
    pickup_point_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    issue_date DATE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (pickup_point_id) REFERENCES PickupPoints(pickup_point_id) ON DELETE RESTRICT
);

CREATE TABLE OrderItems (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    price_at_time DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE RESTRICT
);