CREATE TABLE "users" (
  "id" uuid PRIMARY KEY,
  "first_name" varchar,
  "last_name" varchar,
  "dob" date,
  "age" int,
  "gender" varchar,
  "marital_status" varchar,
  "blood_group" varchar,
  "balance" decimal(10,2),
  "joining_date" date,
  "role_id" uuid
);

CREATE TABLE "roles" (
  "id" uuid PRIMARY KEY,
  "name" varchar,
  "description" text
);

CREATE TABLE "permissions" (
  "id" uuid PRIMARY KEY,
  "name" varchar,
  "description" text
);

CREATE TABLE "role_permissions" (
  "id" uuid PRIMARY KEY,
  "role_id" uuid,
  "permission_id" uuid
);

CREATE TABLE "addresses" (
  "id" uuid PRIMARY KEY,
  "country" varchar,
  "division" varchar,
  "district" varchar,
  "area" varchar
);

CREATE TABLE "budgets" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid,
  "name" varchar,
  "currency" varchar,
  "income_source" varchar,
  "amount" decimal
);

CREATE TABLE "budget_expense_categories" (
  "id" uuid PRIMARY KEY,
  "budget_id" uuid,
  "category_name" varchar,
  "amount" decimal
);

CREATE TABLE "fraud_list" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid,
  "reported_user_id" uuid,
  "reason" varchar
);

CREATE TABLE "contact_info" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid UNIQUE,
  "email" varchar UNIQUE,
  "phone" varchar,
  "address_id" uuid
);

CREATE TABLE "transactions" (
  "id" uuid PRIMARY KEY,
  "amount" decimal(10,2),
  "payment_method" varchar,
  "timestamp" datetime,
  "sender_id" uuid,
  "receiver_id" uuid,
  "note" text,
  "type" enum,
  "location" varchar
);

CREATE TABLE "blockchain" (
  "id" uuid PRIMARY KEY,
  "index" int,
  "type" varchar,
  "timestamp" datetime,
  "previous_hash" varchar,
  "hash" varchar,
  "transaction_id" uuid
);

CREATE TABLE "blockchain_transactions" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid,
  "amount" decimal,
  "current_balance" decimal,
  "method" varchar,
  "timestamp" datetime
);

CREATE TABLE "admin_logs" (
  "id" uuid PRIMARY KEY,
  "admin_id" uuid,
  "ip_address" varchar,
  "timestamp" datetime,
  "details" text
);

CREATE TABLE "budget_expense_items" (
  "id" uuid PRIMARY KEY,
  "category_id" uuid,
  "name" varchar,
  "amount" decimal(10,2),
  "details" text
);

CREATE TABLE "user_expense_habit" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid,
  "timestamp" datetime,
  "monthly_income" varchar,
  "earning_member" boolean,
  "dependents" int,
  "living_situation" varchar,
  "rent" decimal(10,2),
  "transport_mode" varchar,
  "transport_cost" decimal(10,2),
  "eating_out_frequency" varchar,
  "grocery_cost" decimal(10,2),
  "utilities_cost" decimal(10,2),
  "mobile_internet_cost" decimal(10,2),
  "subscriptions" varchar,
  "savings" varchar,
  "investments" text,
  "loans" boolean,
  "loan_payment" decimal(10,2),
  "financial_goal" varchar
);

CREATE TABLE "user_passwords" (
  "user_id" varchar PRIMARY KEY,
  "password" varchar
);

ALTER TABLE "users" ADD FOREIGN KEY ("role_id") REFERENCES "roles" ("id");

ALTER TABLE "role_permissions" ADD FOREIGN KEY ("role_id") REFERENCES "roles" ("id");

ALTER TABLE "role_permissions" ADD FOREIGN KEY ("permission_id") REFERENCES "permissions" ("id");

ALTER TABLE "budgets" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "budget_expense_categories" ADD FOREIGN KEY ("budget_id") REFERENCES "budgets" ("id");

ALTER TABLE "fraud_list" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "fraud_list" ADD FOREIGN KEY ("reported_user_id") REFERENCES "users" ("id");

ALTER TABLE "contact_info" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "contact_info" ADD FOREIGN KEY ("address_id") REFERENCES "addresses" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("sender_id") REFERENCES "users" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("receiver_id") REFERENCES "users" ("id");

ALTER TABLE "blockchain" ADD FOREIGN KEY ("transaction_id") REFERENCES "blockchain_transactions" ("id");

ALTER TABLE "blockchain_transactions" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "admin_logs" ADD FOREIGN KEY ("admin_id") REFERENCES "users" ("id");

ALTER TABLE "budget_expense_items" ADD FOREIGN KEY ("category_id") REFERENCES "budget_expense_categories" ("id");

ALTER TABLE "user_expense_habit" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("timestamp") REFERENCES "budgets" ("income_source");
