# Personal Expense and Budget Tracker — Pseudocode

This pseudocode reflects the structure of `main.py` (and applies equally to
`gui_main.py`, which reuses the same functions). It is organized by function,
matching the required coding tasks in the brief.

---

## 1. LOAD_TRANSACTIONS

```
FUNCTION load_transactions():
    OPEN 'cap-data.csv' for reading
    READ header row to get field names
    CREATE empty list: data

    FOR EACH row in the CSV:
        CONVERT row["amount_kes"] to a float
        CONVERT row["budget_limit_kes"] to a float
        FOR EACH text field in row:
            STRIP leading/trailing whitespace
        row["transaction_type"] <- standardize_transaction_type(row["transaction_type"])
        APPEND row to data

    RETURN data
END FUNCTION
```

---

## 1b. STANDARDIZE_TRANSACTION_TYPE

```
// Only recognized alternatives (defined in TRANSACTION_TYPE_MAP) are
// standardized. Anything not in the map is returned unchanged, so it is
// still correctly caught as "unrecognized transaction_type" by
// validate_transaction() rather than being silently guessed at.
TRANSACTION_TYPE_MAP <- {
    "income": "Income", "inc": "Income", "in": "Income",
    "expense": "Expense", "exp": "Expense", "ex": "Expense"
}

FUNCTION standardize_transaction_type(tx_type):
    key <- tx_type, stripped, lowercased
    IF key is in TRANSACTION_TYPE_MAP:
        RETURN TRANSACTION_TYPE_MAP[key]
    ELSE:
        RETURN tx_type, stripped   // unchanged; will fail validation as unrecognized
END FUNCTION
```

---

## 2. VALIDATE_TRANSACTION (single record)

```
FUNCTION validate_transaction(record):
    CREATE empty list: reasons

    // Rule: type must be Income or Expense
    type <- record["transaction_type"], stripped
    IF type is NOT "Income" AND type is NOT "Expense":
        ADD "unrecognized transaction_type" to reasons

    // Rule: amount must be numeric and > 0
    TRY:
        amount <- CONVERT record["amount_kes"] to float
        IF amount <= 0:
            ADD "amount must be greater than zero" to reasons
    CATCH conversion error:
        ADD "amount must be numeric" to reasons

    // Rule: category required for Expense
    category <- record["category"], stripped
    IF type is "Expense" AND category is empty:
        ADD "missing category for expense" to reasons

    // Rule: budget limit must not be negative
    TRY:
        budget <- CONVERT record["budget_limit_kes"] to float
        IF budget < 0:
            ADD "negative budget limit" to reasons
    CATCH conversion error:
        ADD "budget_limit_kes must be numeric" to reasons

    RETURN reasons   // empty list means the record is valid
END FUNCTION
```

---

## 3. VALIDATE_ALL (whole dataset)

```
FUNCTION validate_all(transactions):
    CREATE empty lists: valid_records, invalid_records

    FOR EACH record in transactions:
        reasons <- validate_transaction(record)
        IF reasons is empty:
            ADD record to valid_records
        ELSE:
            ADD {record, reasons} to invalid_records

    RETURN valid_records, invalid_records
END FUNCTION
```

---

## 4. ADD_TRANSACTION

```
FUNCTION add_transaction(transactions):
    PROMPT for: ID, Category, Description
    PROMPT for: Type
    type <- standardize_transaction_type(Type)   // same mapping as load_transactions

    TRY:
        amount <- CONVERT input "Amount" to float
    CATCH:
        DISPLAY "Invalid amount. Transaction not added."
        RETURN   // exit early, no further prompts

    TRY:
        budget_limit <- CONVERT input "Budget limit" to float
    CATCH:
        DISPLAY "Invalid budget limit. Transaction not added."
        RETURN

    PROMPT for: Payment method

    BUILD new_record from the collected fields
    reasons <- validate_transaction(new_record)

    IF reasons is NOT empty:
        DISPLAY "Transaction rejected" and list the reasons
    ELSE:
        APPEND new_record to transactions
        write_transactions(transactions)
        DISPLAY "Transaction added successfully."
        DISPLAY new_record as a table
END FUNCTION
```

---

## 5. WRITE_TRANSACTIONS

```
FUNCTION write_transactions(transactions):
    IF transactions is empty:
        DISPLAY "No transactions to write."
        RETURN

    OPEN 'cap-data.csv' for writing
    WRITE header row
    WRITE every record in transactions as a CSV row
END FUNCTION
```

---

## 6. SEARCH_TRANSACTION

```
FUNCTION search_transaction(valid_records):
    PROMPT "Search by Transaction ID or Category"
    term <- input, lowercased, stripped
    CREATE empty list: matches

    FOR EACH record in valid_records:
        IF term equals record ID (lowercased)
           OR term equals record category (lowercased):
            ADD record to matches

    IF matches is empty:
        DISPLAY "No matching transactions found."
    ELSE:
        DISPLAY matches as a table
END FUNCTION
```

---

## 7. CALCULATE_SUMMARY

```
FUNCTION calculate_summary(valid_records):
    total_income <- 0
    total_expenditure <- 0
    category_totals <- empty map

    FOR EACH record in valid_records:
        IF record type is "Income":
            total_income <- total_income + amount
        ELSE:
            total_expenditure <- total_expenditure + amount
            ADD amount to category_totals[record category]

    balance <- total_income - total_expenditure
    RETURN total_income, total_expenditure, balance, category_totals
END FUNCTION
```

---

## 8. HIGHEST_SPENDING_CATEGORY

```
FUNCTION highest_spending_category(valid_records):
    (_, _, _, category_totals) <- calculate_summary(valid_records)
    IF category_totals is empty:
        RETURN None, 0

    highest_category <- None
    highest_amount <- None
    FOR EACH (category, total) in category_totals:
        IF highest_amount is None OR total > highest_amount:
            highest_amount <- total
            highest_category <- category

    RETURN highest_category, highest_amount
END FUNCTION
```

---

## 9. CHECK_INDIVIDUAL_BUDGET_WARNINGS

```
FUNCTION check_individual_budget_warnings(valid_records):
    CREATE empty list: warnings

    FOR EACH record in valid_records:
        IF record type is "Expense" AND amount > budget_limit:
            ADD {id, category, amount, limit, over = amount - budget_limit}
                to warnings

    RETURN warnings
END FUNCTION
```

---

## 10. CHECK_CATEGORY_BUDGET_SUMMARY

```
FUNCTION check_category_budget_summary(valid_records):
    category_totals  <- empty map   // spent per category
    category_budgets <- empty map   // combined budget limit per category

    FOR EACH record in valid_records:
        IF record type is "Expense":
            ADD amount to category_totals[category]
            ADD budget_limit to category_budgets[category]

    CREATE empty list: summary
    FOR EACH (category, spent) in category_totals:
        budget <- category_budgets[category]
        status <- "OVER" if spent > budget ELSE "OK"
        ADD {category, spent, budget, over = spent - budget, status}
            to summary

    RETURN summary
END FUNCTION
```

---

## 11. CALCULATE_PAYMENT_METHOD_TOTALS

```
FUNCTION calculate_payment_method_totals(valid_records):
    method_data <- empty map

    FOR EACH record in valid_records:
        method <- record payment_method
        IF method not in method_data:
            method_data[method] <- {count: 0, amount: 0, budget: 0}
        method_data[method].count  <- +1
        method_data[method].amount <- + record amount
        method_data[method].budget <- + record budget_limit

    RETURN method_data
END FUNCTION
```

---

## 12. MAIN PROGRAM LOOP

```
FUNCTION main():
    transactions <- load_transactions()
    (valid_records, invalid_records) <- validate_all(transactions)

    LOOP FOREVER:
        DISPLAY menu:
            1. View valid transactions
            2. Add or search a transaction
            3. View income and expenditure summary
            4. View budget warnings
            5. View invalid records
            6. View payment summary
            7. Exit

        choice <- user input

        CASE choice OF:
            "1": DISPLAY valid_records as a table

            "2": DISPLAY sub-menu (Add / Search)
                 IF sub-choice is "1": CALL add_transaction(transactions)
                 ELSE IF sub-choice is "2": CALL search_transaction(valid_records)
                 ELSE: DISPLAY "Invalid selection."
                 // re-validate, since add_transaction may have changed the data
                 (valid_records, invalid_records) <- validate_all(transactions)

            "3": CALL calculate_summary(valid_records)
                 CALL highest_spending_category(valid_records)
                 DISPLAY the summary

            "4": CALL check_individual_budget_warnings(valid_records)
                 CALL check_category_budget_summary(valid_records)
                 DISPLAY both warning tables

            "5": DISPLAY invalid_records as a table with reasons

            "6": CALL calculate_payment_method_totals(valid_records)
                 DISPLAY the payment summary table

            "7": DISPLAY "Program closed."
                 BREAK loop (exit program)

            DEFAULT: DISPLAY "Invalid selection."
    END LOOP
END FUNCTION

CALL main()
```

---

## Notes

- The **calculation** functions (`calculate_summary`, `highest_spending_category`,
  `check_individual_budget_warnings`, `check_category_budget_summary`,
  `calculate_payment_method_totals`) return data only — they never print or
  prompt. This is intentional: it lets the CLI and GUI share the exact same
  logic and lets each function be tested independently (see the test plan).
- The **display** functions (`display_table`, `display_summary`,
  `display_all_budget_warnings`, `display_payment_summary`,
  `display_invalid_table`) do the printing/formatting and call the
  calculation functions above rather than repeating their logic.
- `validate_transaction()` is the single source of truth for all four
  validation rules, and is called both when loading the CSV at startup
  (`validate_all`) and when adding a new record (`add_transaction`), so
  a record can never bypass validation through either path.
- `standardize_transaction_type()` is likewise called from both entry
  points (`load_transactions` and `add_transaction`), *before*
  validation runs, so a recognized alias (e.g. `"EXP"`) is normalized
  the same way whether it comes from the CSV or from user input. Only
  aliases explicitly listed in `TRANSACTION_TYPE_MAP` are touched;
  anything else is passed through unchanged and correctly rejected by
  `validate_transaction()` as an unrecognized type.
