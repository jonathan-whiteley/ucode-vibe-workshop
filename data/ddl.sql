-- LCE Operator Command Center: Workshop schema
-- Run in: ioc_sandbox.vibe_workshop

USE CATALOG ioc_sandbox;
CREATE SCHEMA IF NOT EXISTS vibe_workshop;
USE SCHEMA vibe_workshop;

-- DIMS ----------------------------------------------------------------------

CREATE OR REPLACE TABLE dims_stores (
  store_id        STRING NOT NULL,
  store_name      STRING,
  region          STRING,
  city            STRING,
  state           STRING,
  square_footage  INT
);

CREATE OR REPLACE TABLE dims_items (
  sku           STRING NOT NULL,
  item_name     STRING,
  category      STRING,
  retail_price  DECIMAL(10,2),
  cost          DECIMAL(10,2)
);

-- FACTS ---------------------------------------------------------------------

CREATE OR REPLACE TABLE facts_labor_daily (
  date         DATE,
  store_id     STRING,
  role         STRING,
  headcount    INT,
  total_hours  DOUBLE,
  labor_cost   DECIMAL(10,2)
);

CREATE OR REPLACE TABLE facts_sales_inventory_daily (
  date           DATE,
  store_id       STRING,
  sku            STRING,
  units_sold     INT,
  revenue        DECIMAL(10,2),
  on_hand_eod    INT,
  reorder_point  INT
);

CREATE OR REPLACE TABLE facts_customer_feedback (
  feedback_id    STRING,
  date           DATE,
  store_id       STRING,
  channel        STRING,
  rating         INT,
  feedback_text  STRING,
  nps            INT
);
