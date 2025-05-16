-- public.categories определение

-- Drop table

-- DROP TABLE categories;

CREATE TABLE categories (
	category_id serial4 NOT NULL,
	"name" varchar(512) NOT NULL,
	CONSTRAINT categories_pkey PRIMARY KEY (category_id)
);



-- public.deliveries определение

-- Drop table

-- DROP TABLE deliveries;

CREATE TABLE deliveries (
	delivery_id serial4 NOT NULL, -- Уникальный идентификатор поставки
	supplier_id int4 NULL, -- Идентификатор поставщика
	delivery_date date NOT NULL, -- Дата привоза
	CONSTRAINT deliveries_pkey PRIMARY KEY (delivery_id)
);
COMMENT ON TABLE public.deliveries IS 'Данные о привозах продуктов';

-- Column comments

COMMENT ON COLUMN public.deliveries.delivery_id IS 'Уникальный идентификатор поставки';
COMMENT ON COLUMN public.deliveries.supplier_id IS 'Идентификатор поставщика';
COMMENT ON COLUMN public.deliveries.delivery_date IS 'Дата привоза';


-- public.deliveries внешние включи

ALTER TABLE public.deliveries ADD CONSTRAINT deliveries_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE CASCADE;





-- public.delivery_contents определение

-- Drop table

-- DROP TABLE delivery_contents;

CREATE TABLE delivery_contents (
	delivery_content_id serial4 NOT NULL, -- Уникальный идентификатор строки поставки
	delivery_id int4 NULL, -- Идентификатор поставки
	barcode varchar(20) NULL, -- Штрихкод продукта
	quantity int4 NOT NULL, -- Количество продукта в поставке
	CONSTRAINT delivery_contents_pkey PRIMARY KEY (delivery_content_id)
);
COMMENT ON TABLE public.delivery_contents IS 'Состав поставки продуктов';

-- Column comments

COMMENT ON COLUMN public.delivery_contents.delivery_content_id IS 'Уникальный идентификатор строки поставки';
COMMENT ON COLUMN public.delivery_contents.delivery_id IS 'Идентификатор поставки';
COMMENT ON COLUMN public.delivery_contents.barcode IS 'Штрихкод продукта';
COMMENT ON COLUMN public.delivery_contents.quantity IS 'Количество продукта в поставке';


-- public.delivery_contents внешние включи

ALTER TABLE public.delivery_contents ADD CONSTRAINT delivery_contents_barcode_fkey FOREIGN KEY (barcode) REFERENCES products(barcode) ON DELETE CASCADE;
ALTER TABLE public.delivery_contents ADD CONSTRAINT delivery_contents_delivery_id_fkey FOREIGN KEY (delivery_id) REFERENCES deliveries(delivery_id) ON DELETE CASCADE;




-- public.price_audit определение

-- Drop table

-- DROP TABLE price_audit;

CREATE TABLE price_audit (
	id serial4 NOT NULL,
	barcode varchar(255) NULL,
	old_price numeric NULL,
	new_price numeric NULL,
	update_time timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT price_audit_pkey PRIMARY KEY (id)
);





-- public.prices определение

-- Drop table

-- DROP TABLE prices;

CREATE TABLE prices (
	price_id serial4 NOT NULL,
	barcode varchar(20) NULL,
	start_date date NOT NULL,
	end_date date NULL,
	price numeric NOT NULL,
	CONSTRAINT prices_pkey PRIMARY KEY (price_id)
);

-- Table Triggers

create trigger price_update_trigger after
update
    on
    public.prices for each row
    when ((old.price is distinct
from
    new.price)) execute function audit_price_change();


-- public.prices внешние включи

ALTER TABLE public.prices ADD CONSTRAINT prices_barcode_fkey FOREIGN KEY (barcode) REFERENCES products(barcode) ON DELETE CASCADE;





-- public.products определение

-- Drop table

-- DROP TABLE products;

CREATE TABLE products (
	barcode varchar(20) NOT NULL,
	"name" varchar(512) NULL,
	package_size varchar(50) NULL,
	weight numeric NULL,
	category_id int4 NULL,
	CONSTRAINT products_pkey PRIMARY KEY (barcode)
);


-- public.products внешние включи

ALTER TABLE public.products ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE;






-- public.sales определение

-- Drop table

-- DROP TABLE sales;

CREATE TABLE sales (
	sale_id serial4 NOT NULL,
	user_id int4 NULL,
	total_sum numeric(10, 2) NULL,
	sale_date date NOT NULL,
	address varchar(255) NULL,
	phone_number varchar(15) NULL,
	CONSTRAINT sales_pkey PRIMARY KEY (sale_id)
);


-- public.sales внешние включи

ALTER TABLE public.sales ADD CONSTRAINT sales_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE;








-- public.sales_details определение

-- Drop table

-- DROP TABLE sales_details;

CREATE TABLE sales_details (
	sale_id int4 NULL,
	barcode varchar(20) NULL,
	quantity int4 NOT NULL,
	price_per_piece numeric(10, 2) NULL,
	total_price numeric(10, 2) NULL
);


-- public.sales_details внешние включи

ALTER TABLE public.sales_details ADD CONSTRAINT sales_details_barcode_fkey FOREIGN KEY (barcode) REFERENCES products(barcode) ON DELETE CASCADE;
ALTER TABLE public.sales_details ADD CONSTRAINT sales_details_sale_id_fkey FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE;





-- public.suppliers определение

-- Drop table

-- DROP TABLE suppliers;

CREATE TABLE suppliers (
	supplier_id serial4 NOT NULL,
	"name" varchar(100) NOT NULL,
	phone varchar(20) NULL,
	address varchar(255) NULL,
	CONSTRAINT suppliers_pkey PRIMARY KEY (supplier_id)
);







-- public.users определение

-- Drop table

-- DROP TABLE users;

CREATE TABLE users (
	user_id serial4 NOT NULL,
	username varchar(50) NOT NULL,
	password_hash varchar(255) NOT NULL,
	"role" varchar(20) NOT NULL,
	email varchar(100) NULL,
	active bool DEFAULT true NULL,
	CONSTRAINT users_email_key UNIQUE (email),
	CONSTRAINT users_pkey PRIMARY KEY (user_id),
	CONSTRAINT users_role_check CHECK (((role)::text = ANY ((ARRAY['admin'::character varying, 'editor'::character varying, 'user'::character varying])::text[]))),
	CONSTRAINT users_username_key UNIQUE (username)
);


