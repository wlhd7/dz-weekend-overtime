/*
DROP TABLE IF EXISTS departments;
*/
-- canonical schema: standardized department and sub-department FKs
DROP TABLE IF EXISTS staffs;
DROP TABLE IF EXISTS departments;
DROP TABLE IF EXISTS sub_departments;
DROP TABLE IF EXISTS sat;
DROP TABLE IF EXISTS sun;

CREATE TABLE IF NOT EXISTS departments (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS sub_departments (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	department_id INTEGER NOT NULL,
	name TEXT NOT NULL,
	UNIQUE(department_id, name),
	FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE IF NOT EXISTS staffs (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE NOT NULL,
	department_id INTEGER NOT NULL,
	sub_department_id INTEGER,
	FOREIGN KEY (department_id) REFERENCES departments(id),
	FOREIGN KEY (sub_department_id) REFERENCES sub_departments(id)
);

CREATE TABLE IF NOT EXISTS sat (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	staff_id INTEGER NOT NULL,
	is_evection BOOLEAN DEFAULT 0,
	updated_at INTEGER DEFAULT (CAST(strftime('%d','now','+8 hours') AS INTEGER)),
	FOREIGN KEY (staff_id) REFERENCES staffs(id)
);

CREATE TABLE IF NOT EXISTS sun (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	staff_id INTEGER NOT NULL,
	is_evection BOOLEAN DEFAULT 0,
	updated_at INTEGER DEFAULT (CAST(strftime('%d','now','+8 hours') AS INTEGER)),
	FOREIGN KEY (staff_id) REFERENCES staffs(id)
);