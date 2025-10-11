drop table if exists staffs;
CREATE TABLE IF NOT EXISTS staffs (
	id integer primary key autoincrement,
	name text unique not null,
	department text not null,
	sub_department text
);
