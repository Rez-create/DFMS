CREATE DATABASE dfms;

USE dfms;

-- Central animal registration
CREATE TABLE animal (
    ear_tag         VARCHAR(20)  PRIMARY KEY,
    cow_name        VARCHAR(100) NOT NULL,
    animal_type     VARCHAR(10)  NOT NULL DEFAULT 'Cow',
    breed           VARCHAR(50)  NOT NULL,
    color           VARCHAR(30)  NOT NULL,
    birth_date      DATE         NOT NULL
);

-- Milk produced per animal
CREATE TABLE milkrecord (
    record_id               VARCHAR(20)  PRIMARY KEY,
    milking_date            DATE         NOT NULL,
    animal_ear_tag          VARCHAR(20)  NOT NULL,
    morning_milk_quantity   FLOAT,
    afternoon_milk_quantity FLOAT        DEFAULT 0,
    evening_milk_quantity   FLOAT        DEFAULT 0,
    FOREIGN KEY (animal_ear_tag) REFERENCES core_animal(ear_tag)
);

-- Milk sold, linked to a milk record
CREATE TABLE milksale (
    sale_id         VARCHAR(20)     PRIMARY KEY,
    record_id       VARCHAR(20)     NOT NULL,
    sale_date    DATE            NOT NULL,
    unit_price      DECIMAL(10,2)   NOT NULL,
    client_name     VARCHAR(100)    NOT NULL,
    client_contact  VARCHAR(15)     NOT NULL,
    amount_bought   FLOAT           NOT NULL,
    total_price     DECIMAL(10,2)   NOT NULL DEFAULT 0.00,
    FOREIGN KEY (record_id) REFERENCES core_milkrecord(record_id)
);

-- Farm expenses (feed purchases, labor, vet)
CREATE TABLE farmfinance (
    finance_id      VARCHAR(20)   PRIMARY KEY,
    date_incurred   DATE          NOT NULL,
    expense_type    VARCHAR(20)   DEFAULT 'Other',
    amount_incurred DECIMAL(10,2) NOT NULL
);


CREATE TABLE employee (
    employee_id     VARCHAR(10)  PRIMARY KEY,
    employee_name   VARCHAR(100) NOT NULL,
    gender          VARCHAR(6)   NOT NULL,
    phone_number    VARCHAR(15)  NOT NULL,
    address         TEXT         NOT NULL,
    designation     VARCHAR(20)  DEFAULT 'Milker',
    date_hired      DATE         NOT NULL,
    finance_id      VARCHAR(20),
    FOREIGN KEY (finance_id) REFERENCES core_farmfinance(finance_id)
);

-- Breeding records, linked to animal and supervised by employee
CREATE TABLE breeding (
    breeding_id                 VARCHAR(20)  PRIMARY KEY,
    animal_ear_tag              VARCHAR(20)  NOT NULL,
    supervised_by               VARCHAR(10),
    heat_date                   DATE,
    breeding_date               DATE         NOT NULL,
    bull_name                   VARCHAR(100) NOT NULL,
    pregnancy_diagnosis_date    DATE,
    date_due_to_calve           DATE,
    date_calved                 DATE,
    age_of_cow_at_calving       INTEGER,
    calf_name                   VARCHAR(100),
    calving_notes               TEXT,
    FOREIGN KEY (animal_ear_tag) REFERENCES core_animal(ear_tag),
    FOREIGN KEY (supervised_by) REFERENCES core_employee(employee_id)
);

-- Stock feeds linked to a finance record (feed purchase = expense)
CREATE TABLE stockfeed (
    feed_id             VARCHAR(20)   PRIMARY KEY,
    finance_id          VARCHAR(20),
    feed_type           VARCHAR(50)   NOT NULL,
    quantity            DECIMAL(10,2) NOT NULL,
    unit_of_measurement VARCHAR(15)   NOT NULL,
    supplier_name       VARCHAR(100)  NOT NULL,
    supplier_contact    VARCHAR(100),
    supplier_phone      VARCHAR(15),
    purchase_date       DATE          NOT NULL,
    expiration_date     DATE,
    cost_per_unit       DECIMAL(10,2) NOT NULL,
    notes               TEXT,
    total_cost          DECIMAL(10,0) NOT NULL DEFAULT 0,
    FOREIGN KEY (finance_id) REFERENCES core_farmfinance(finance_id)
);

-- ============================================================
-- RELATIONSHIPS SUMMARY
-- core_milkrecord.animal_ear_tag  -> core_animal.ear_tag       (Many-to-One)
-- core_milksale.record_id         -> core_milkrecord.record_id (Many-to-One)
-- core_breeding.animal_ear_tag    -> core_animal.ear_tag       (Many-to-One)
-- core_breeding.supervised_by     -> core_employee.employee_id (Many-to-One)
-- core_employee.finance_id        -> core_farmfinance.finance_id (Many-to-One)
-- core_stockfeed.finance_id       -> core_farmfinance.finance_id (Many-to-One)


