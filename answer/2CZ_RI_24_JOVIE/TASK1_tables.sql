CREATE TABLE CUSTOMERS(
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT
);
CREATE TABLE PRODUCTS(
    product_id integer PRIMARY KEY,
    name TEXT,
    model TEXT,
    category TEXT,
    price INTEGER,
    stock INTEGER
);
CREATE TABLE ORDERS (
	order_id	INTEGER,
	customer_id	INTEGER,
    product_id  INTEGER
	quantity    INTEGER,
	order_date	TEXT,
	PRIMARY KEY(order_id, product_id),
	FOREIGN KEY(customer_id) REFERENCES CUSTOMERS(customer_id),
	FOREIGN KEY(product_id) REFERENCES PRODUCTS(product_id)
);