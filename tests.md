# Personal Expense and Budget Tracker - Test Cases

## Test Plan Overview

This document contains documented test cases covering the five required categories:
1. **Normal** — valid records process successfully
2. **Invalid** — invalid records are rejected with reasons
3. **Boundary** — edge cases at classification limits
4. **Search** — finding existing and non-existing records
5. **Menu** — invalid menu options and exit behavior

---

## Test 1: Normal Operation — Valid Transaction Accepted

| Attribute | Value |
|-----------|-------|
| **Test ID** | T001 |
| **Category** | Normal |
| **Objective** | Verify that a complete, valid transaction is accepted and added |
| **Input** | New transaction via add option:<br>- ID: TX999<br>- Type: Expense<br>- Category: Food<br>- Description: Groceries<br>- Amount: 2500.00<br>- Budget: 5000.00<br>- Payment: Card |
| **Expected Result** | Transaction validates successfully, is appended to transactions list, written to CSV file, user sees "Transaction added successfully." message |
| **Actual Result** | Transaction passes all validation checks, CSV file updated with new row, success message displayed |
| **Status** | **PASS** |
| **Notes** | All fields meet requirements; no validation rules violated |

---

## Test 2: Invalid Operation — Missing Required Category

| Attribute | Value |
|-----------|-------|
| **Test ID** | T002 |
| **Category** | Invalid |
| **Objective** | Verify that an Expense transaction without a category is rejected |
| **Input** | New transaction via add option:<br>- ID: TX998<br>- Type: Expense<br>- Category: (empty)<br>- Description: Office supplies<br>- Amount: 1500.00<br>- Budget: 2000.00<br>- Payment: Bank |
| **Expected Result** | Validation fails; user sees rejection message: "Transaction rejected: - missing category for expense" |
| **Actual Result** | Validation identifies missing category; transaction not added; rejection message displayed; user returns to menu |
| **Status** | **PASS** |
| **Notes** | Category is required for all Expense records; validation correctly enforces this rule |

---

## Test 3: Invalid Operation — Negative Amount

| Attribute | Value |
|-----------|-------|
| **Test ID** | T003 |
| **Category** | Invalid |
| **Objective** | Verify that a transaction with a negative amount is rejected |
| **Input** | Transaction record from CSV (TX005):<br>- ID: TX005<br>- Type: Expense<br>- Category: Entertainment<br>- Amount: -2500.00<br>- Budget: 3000.00 |
| **Expected Result** | Validation fails during load; record classified as invalid; rejection reason: "amount must be greater than zero"; record listed in Option 5 (invalid records) |
| **Actual Result** | Validation correctly identifies negative amount, rejects record, displays reason in invalid records list |
| **Status** | **PASS** |
| **Notes** | Amounts must be strictly > 0; negative and zero values are both rejected |

---

## Test 4: Boundary Test — Amount Exactly Equal to Budget Limit

| Attribute | Value |
|-----------|-------|
| **Test ID** | T004 |
| **Category** | Boundary |
| **Objective** | Verify that a transaction with amount equal to (but not exceeding) budget limit is not flagged |
| **Input** | Valid transaction:<br>- ID: TX997<br>- Type: Expense<br>- Category: Transport<br>- Amount: 5000.00<br>- Budget: 5000.00 |
| **Expected Result** | Transaction is valid and accepted; amount equals budget limit, so NOT flagged in individual budget warnings; transaction appears in Option 1 (valid records) |
| **Actual Result** | Transaction passes validation; amount = budget (5000 = 5000) is acceptable; no warning generated for this transaction |
| **Status** | **PASS** |
| **Notes** | Condition is `if amount > budget`, not `>=`; equal amounts do not trigger warnings |

---

## Test 5: Boundary Test — Amount Just Over Budget Limit

| Attribute | Value |
|-----------|-------|
| **Test ID** | T005 |
| **Category** | Boundary |
| **Objective** | Verify that a transaction just over its budget limit is flagged |
| **Input** | Valid transaction:<br>- ID: TX996<br>- Type: Expense<br>- Category: Transport<br>- Amount: 5000.01<br>- Budget: 5000.00 |
| **Expected Result** | Transaction is valid and accepted; but amount exceeds budget limit (5000.01 > 5000); flagged in Option 4 (individual budget warnings) with "over by 0.01" |
| **Actual Result** | Transaction passes validation; individual budget warning generated; correctly shows overage of 0.01 |
| **Status** | **PASS** |
| **Notes** | Boundary condition is strict `>` comparison; even 0.01 overage is detected |

---

## Test 6: Search Operation — Existing Transaction by ID

| Attribute | Value |
|-----------|-------|
| **Test ID** | T006 |
| **Category** | Search |
| **Objective** | Verify that search by transaction ID returns the matching record(s) |
| **Input** | Via Option 2 → 2 (search):<br>Search term: "TX001" |
| **Expected Result** | Search finds transaction TX001; displays it in table format with all fields (ID, Type, Category, Description, Amount, Budget, Payment) |
| **Actual Result** | Query executed; matching record found and displayed in formatted table |
| **Status** | **PASS** |
| **Notes** | Search is case-insensitive; exact match on ID or category name |

---

## Test 7: Search Operation — Non-Existing Transaction

| Attribute | Value |
|-----------|-------|
| **Test ID** | T007 |
| **Category** | Search |
| **Objective** | Verify that search for a non-existent record returns appropriate message |
| **Input** | Via Option 2 → 2 (search):<br>Search term: "TX404" (does not exist in valid records) |
| **Expected Result** | Search completes; no matching records found; user sees "No matching transactions found." message; menu repeats |
| **Actual Result** | Query executed; zero matches identified; appropriate message displayed; control returns to menu |
| **Status** | **PASS** |
| **Notes** | Both ID and category are searched; if neither matches, message is shown |

---

## Test 8: Search Operation — Multiple Records by Category

| Attribute | Value |
|-----------|-------|
| **Test ID** | T008 |
| **Category** | Search |
| **Objective** | Verify that search by category returns all transactions in that category |
| **Input** | Via Option 2 → 2 (search):<br>Search term: "Transport" |
| **Expected Result** | Search finds all Expense transactions with category "Transport"; displays multiple rows in table (TX001, TX007, TX013, TX019, etc.) |
| **Actual Result** | Query executed; all Transport category transactions found and displayed in formatted table with alignment |
| **Status** | **PASS** |
| **Notes** | Category search is case-insensitive and matches all transactions in that category |

---

## Test 9: Menu Control — Invalid Menu Option

| Attribute | Value |
|-----------|-------|
| **Test ID** | T009 |
| **Category** | Menu |
| **Objective** | Verify that invalid menu input is rejected and menu repeats |
| **Input** | At main menu prompt "Enter selection:"<br>User enters: "9" (not a valid option 1–7) |
| **Expected Result** | Menu displays "Invalid selection." message; menu repeats; user can enter another option |
| **Actual Result** | Invalid input detected; error message shown; menu loop continues; user returned to menu prompt |
| **Status** | **PASS** |
| **Notes** | Only options 1–7 are valid; any other input (including empty, letters, special chars) is rejected |

---

## Test 10: Menu Control — Exit Option Terminates Program

| Attribute | Value |
|-----------|-------|
| **Test ID** | T010 |
| **Category** | Menu |
| **Objective** | Verify that selecting Option 7 (Exit) terminates the program cleanly |
| **Input** | At main menu, user selects: "7" |
| **Expected Result** | Program displays "Program closed." message and exits the menu loop; process terminates cleanly |
| **Actual Result** | Option 7 triggers break statement; "Program closed." message displayed; while loop exits; script ends |
| **Status** | **PASS** |
| **Notes** | All data has been persisted to CSV via write operations; exit is safe |

---

## Test 11: Data Validation — Unrecognized Transaction Type

| Attribute | Value |
|-----------|-------|
| **Test ID** | T011 |
| **Category** | Invalid |
| **Objective** | Verify that an unrecognized transaction type is rejected |
| **Input** | Transaction record from CSV (TX011):<br>- ID: TX011<br>- Type: "EXP" (not "Expense")<br>- Category: Entertainment<br>- Amount: 8409<br>- Budget: 5500 |
| **Expected Result** | Validation fails; rejection reason: "unrecognized transaction_type: 'EXP'"; record listed in Option 5 (invalid records) |
| **Actual Result** | Validation correctly identifies unrecognized type; rejects record; rejection reason displayed in invalid list |
| **Status** | **PASS** |
| **Notes** | Only "Income" and "Expense" (exact case) are valid; no auto-mapping or abbreviations accepted |

---

## Test 12: Data Validation — Non-Numeric Amount

| Attribute | Value |
|-----------|-------|
| **Test ID** | T012 |
| **Category** | Invalid |
| **Objective** | Verify that non-numeric amount input is rejected at add time |
| **Input** | Via Option 2 → 1 (add):<br>User attempts to enter: "two thousand" for amount |
| **Expected Result** | ValueError caught; message displayed: "Invalid amount. Transaction not added."; function returns early; menu repeats |
| **Actual Result** | try-except block catches ValueError; user-friendly message shown; transaction not added; menu repeats |
| **Status** | **PASS** |
| **Notes** | Float conversion is attempted; if it fails, transaction is rejected without crashing the program |

---

## Test 13: Summary Calculation — Correct Income/Expenditure Totals

| Attribute | Value |
|-----------|-------|
| **Test ID** | T013 |
| **Category** | Normal |
| **Objective** | Verify that income and expenditure totals are calculated correctly |
| **Input** | Option 3 (view summary) on sample dataset with known totals |
| **Expected Result** | Summary displays:<br>- Total Income = sum of all "Income" transactions<br>- Total Expenditure = sum of all "Expense" transactions<br>- Balance = Income - Expenditure<br>- Category breakdown shows per-category sums |
| **Actual Result** | Calculation function correctly aggregates valid records; totals match expected values; balance formula applied correctly |
| **Status** | **PASS** |
| **Notes** | Only valid records are included; invalid records are excluded from calculations |

---

## Test 14: Budget Warnings — Individual and Category Levels

| Attribute | Value |
|-----------|-------|
| **Test ID** | T014 |
| **Category** | Normal |
| **Objective** | Verify that budget warnings are generated at both individual and category levels |
| **Input** | Option 4 (view budget warnings) on sample data |
| **Expected Result** | **Individual warnings:** list transactions where amount > their budget limit<br>**Category summary:** list categories where total spent > total budgets<br>Both displayed in formatted tables with "Over by" column |
| **Actual Result** | Individual warnings correctly identify overspending transactions; category summary correctly sums and compares per-category; both displayed with proper formatting |
| **Status** | **PASS** |
| **Notes** | Two separate checks run; both results displayed; provides comprehensive budget oversight |

---

## Test Summary

| Test ID | Category | Description | Status |
|---------|----------|-------------|--------|
| T001 | Normal | Valid transaction accepted | PASS |
| T002 | Invalid | Missing category rejected | PASS |
| T003 | Invalid | Negative amount rejected | PASS |
| T004 | Boundary | Amount = budget limit (no warning) | PASS |
| T005 | Boundary | Amount just over limit (warning) | PASS |
| T006 | Search | Search by existing ID | PASS |
| T007 | Search | Search for non-existent record | PASS |
| T008 | Search | Search by category (multiple results) | PASS |
| T009 | Menu | Invalid menu option rejected | PASS |
| T010 | Menu | Exit option terminates program | PASS |
| T011 | Invalid | Unrecognized transaction type | PASS |
| T012 | Invalid | Non-numeric amount at add time | PASS |
| T013 | Normal | Summary calculations correct | PASS |
| T014 | Normal | Budget warnings generated correctly | PASS |

**Total Tests:** 14  
**Passed:** 14  
**Failed:** 0  
**Success Rate:** 100%

---

## Test Execution Notes

- All tests were executed against the current version of `main.py` with `cap-data.csv`.
- Invalid records (T002, T003, T011, T012) are caught at validation time and do not crash the program.
- Menu control (T009, T010) ensures the loop is robust and exits cleanly.
- Search (T006–T008) handles both single and multiple results gracefully.
- Budget calculations (T013–T014) verify the two-level approach (individual and category) works correctly.
- Boundary tests (T004–T005) confirm that comparison operators are strict (`>`, not `>=`).

All core functionality has been tested and verified to work as documented in README.md and PSEUDOCODE.md.
