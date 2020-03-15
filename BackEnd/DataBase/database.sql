 -- Create tables
CREATE TABLE product(
	id INTEGER PRIMARY KEY NOT NULL,
	name TEXT NOT NULL,
	ingred TEXT,
	calories REAL,
	trans_fat REAL,
	satu_fat REAL,
	tot_fat REAL,
	sodium REAL,
	cholesterol REAL,
	tot_carhy REAL,
	diet_fiber REAL,
	protein REAL,
	sugars REAL,
	labels TEXT,
	serv_size TEXT,
	tot_ser REAL,
	store CHAR(10) NOT NULL
);

CREATE TABLE store(
	id INTEGER PRIMARY KEY NOT NULL,
	name CHAR(10) NOT NULL,
	address TEXT NOT NULL,
	city CHAR(20),
	state CHAR(20),
	zipcode CHAR(8),
	FOREIGN KEY(name) REFERENCES product(store)
);


-- Import csv files into tables
.separator ","
.import "store.csv" store

.separator ","
.import "product.csv" product

-- Set NULL values
UPDATE product SET ingred=NULL WHERE ingred="";
UPDATE product SET calories=NULL WHERE calories="";
UPDATE product SET trans_fat=NULL WHERE trans_fat="";
UPDATE product SET satu_fat=NULL WHERE satu_fat="";
UPDATE product SET tot_fat=NULL WHERE tot_fat="";
UPDATE product SET sodium=NULL WHERE sodium="";
UPDATE product SET cholesterol=NULL WHERE cholesterol="";
UPDATE product SET tot_carhy=NULL WHERE tot_carhy="";
UPDATE product SET diet_fiber=NULL WHERE diet_fiber="";
UPDATE product SET protein=NULL WHERE protein="";
UPDATE product SET sugars=NULL WHERE sugars="";
UPDATE product SET labels=NULL WHERE labels="";
UPDATE product SET serv_size=NULL WHERE serv_size="";
UPDATE product SET tot_ser=NULL WHERE tot_ser="";

