# Personal Expense and Budget Tracker — Test Cases

## Test Plan Overview

This document contains documented test cases covering the five required categories:

1. **Normal** — valid records process successfully
2. **Invalid** — invalid records are rejected with reasons
3. **Boundary** — edge cases at classification limits
4. **Search** — finding existing and non-existing records
5. **Menu** — invalid menu options and exit behaviour

### How these tests were executed

Every test below was run against `main.py` with the unmodified `cap-data.csv`.
Each **Evidence** block is a captured terminal transcript of the real session —
the values shown after each prompt are the inputs typed by the tester.

To reproduce any test, run the program and enter the inputs listed in the
**Input** row:

```bash
python3 main.py
```

Repeated menu re-displays between steps are elided as `[menu redisplayed]` to
keep transcripts readable. Nothing else has been altered.

**Baseline:** `cap-data.csv` contains 21 records — **18 valid, 3 invalid**.

---

## Test 1: Normal Operation — Valid Transaction Accepted

| Attribute | Value |
|-----------|-------|
| **Test ID** | T001 |
| **Category** | Normal |
| **Objective** | Verify that a complete, valid transaction is accepted, added and persisted |
| **Input** | Menu 2 → 1 (add):<br>ID: TX999, Type: Expense, Category: Food, Description: Groceries, Amount: 2500, Budget: 5000, Payment: Card |
| **Expected Result** | Transaction validates, is appended to the list, written to CSV, and "Transaction added successfully." is displayed |
| **Actual Result** | As expected — success message displayed and new row written to `cap-data.csv` (see evidence) |
| **Status** | **PASS** |
| **Notes** | All fields meet the validation rules; no rules violated |

### Evidence

```
Enter selection: 2
1. Add a transaction
2. Search a transaction
Enter selection: 1


--- Add new transaction ---


Transaction ID: TX999
Type (Income/Expense): Expense
Category: Food
Description: Groceries
Amount (KES): 2500
Budget limit (KES): 5000
Payment method: Card
Transaction added successfully.
```

Persistence confirmed — last line of `cap-data.csv` after the session:

```
$ tail -1 cap-data.csv
TX999,Expense,Food,Groceries,2500.0,5000.0,Card
```

**Code path exercised:** `add_transaction()` → `validate_transaction()` returns
`[]` → `transactions.append(new_record)` → `write_transactions()`.

---

## Test 2: Invalid Operation — Missing Required Category

| Attribute | Value |
|-----------|-------|
| **Test ID** | T002 |
| **Category** | Invalid |
| **Objective** | Verify that an Expense transaction without a category is rejected |
| **Input** | Menu 2 → 1 (add):<br>ID: TX998, Type: Expense, Category: *(empty)*, Description: Office supplies, Amount: 1500, Budget: 2000, Payment: Bank |
| **Expected Result** | Validation fails; "Transaction rejected: - missing category for expense" displayed; record not added |
| **Actual Result** | As expected — rejection message displayed, record not appended, control returned to menu |
| **Status** | **PASS** |
| **Notes** | Category is mandatory for Expense records; the rule is enforced at add time |

### Evidence

```
Enter selection: 2
1. Add a transaction
2. Search a transaction
Enter selection: 1


--- Add new transaction ---


Transaction ID: TX998
Type (Income/Expense): Expense
Category: 
Description: Office supplies
Amount (KES): 1500
Budget limit (KES): 2000
Payment method: Bank
Transaction rejected:
 - missing category for expense
```

**Code path exercised:** `validate_transaction()` →
`if tx_type.lower() == "expense" and not category` → reason appended → caller
prints reasons and skips `append`.

---

## Test 3: Invalid Operation — Negative Amount

| Attribute | Value |
|-----------|-------|
| **Test ID** | T003 |
| **Category** | Invalid |
| **Objective** | Verify that a record with a negative amount is rejected at load time |
| **Input** | Existing CSV record TX005 (amount = -2500.0), viewed via Menu option 5 |
| **Expected Result** | Record classified invalid with reason "amount must be greater than zero" and listed under invalid records |
| **Actual Result** | As expected — TX005 listed with the correct reason |
| **Status** | **PASS** |
| **Notes** | Amounts must be strictly greater than zero; zero and negative are both rejected |

### Evidence

```
Enter selection: 5
TX005 - amount must be greater than zero
TX011 - unrecognized transaction_type: 'EXP'
TX016 - missing category for expense
```

TX005 is also absent from the valid-records table in Test 13's evidence,
confirming it is excluded from all calculations.

---

## Test 4: Boundary Test — Amount Exactly Equal to Budget Limit

| Attribute | Value |
|-----------|-------|
| **Test ID** | T004 |
| **Category** | Boundary |
| **Objective** | Verify a transaction whose amount **equals** its budget limit is accepted and **not** flagged |
| **Input** | Menu 2 → 1 (add): ID: TX997, Type: Expense, Category: Transport, Description: Boundary equal, Amount: 5000, Budget: 5000, Payment: Card<br>Then Menu option 4 (budget warnings) |
| **Expected Result** | Transaction accepted; TX997 does **not** appear in the individual warnings table |
| **Actual Result** | As expected — added successfully, and absent from the warnings table |
| **Status** | **PASS** |
| **Notes** | The comparison is `amount > budget`, not `>=`, so equality does not trigger a warning |

### Evidence

```
Transaction ID: TX997
Type (Income/Expense): Expense
Category: Transport
Description: Boundary equal
Amount (KES): 5000
Budget limit (KES): 5000
Payment method: Card
Transaction added successfully.

[menu redisplayed]

Enter selection: 4

================================================================================
INDIVIDUAL TRANSACTION WARNINGS
================================================================================
ID         Category        Amount       Limit        Over by     
--------------------------------------------------------------------------------
TX010      Education       7690         3000         4690        
TX015      Utilities       11285        3000         8285        
TX017      Entertainment   12723        8000         4723        
TX019      Transport       14161        13000        1161        
TX020      Housing         14880        3000         11880       
================================================================================
```

**TX997 is absent from the warnings table** — this absence is the result being
tested. The five pre-existing warnings are unchanged, confirming the new record
was processed but correctly not flagged.

---

## Test 5: Boundary Test — Amount Just Over Budget Limit

| Attribute | Value |
|-----------|-------|
| **Test ID** | T005 |
| **Category** | Boundary |
| **Objective** | Verify a transaction marginally **over** its budget limit is flagged |
| **Input** | Menu 2 → 1 (add): ID: TX996, Type: Expense, Category: Transport, Description: Boundary over, Amount: 5000.01, Budget: 5000, Payment: Card<br>Then Menu option 4 (budget warnings) |
| **Expected Result** | Transaction accepted; TX996 **appears** in the individual warnings table |
| **Actual Result** | As expected — TX996 appears as a sixth row. **However, the overage displays as `0` rather than `0.01`** (see defect note) |
| **Status** | **PASS** (detection) / **DEFECT FOUND** (display) |
| **Notes** | Detection logic is correct at 0.01 resolution; the display format loses sub-unit precision |

### Evidence

```
Transaction ID: TX996
Type (Income/Expense): Expense
Category: Transport
Description: Boundary over
Amount (KES): 5000.01
Budget limit (KES): 5000
Payment method: Card
Transaction added successfully.

[menu redisplayed]

Enter selection: 4

================================================================================
INDIVIDUAL TRANSACTION WARNINGS
================================================================================
ID         Category        Amount       Limit        Over by     
--------------------------------------------------------------------------------
TX010      Education       7690         3000         4690        
TX015      Utilities       11285        3000         8285        
TX017      Entertainment   12723        8000         4723        
TX019      Transport       14161        13000        1161        
TX020      Housing         14880        3000         11880       
TX996      Transport       5000         5000         0           
================================================================================
```

### Defect found — display precision

TX996 is correctly flagged, proving the `>` comparison detects a 0.01 overage.
But the printed row reads `5000  5000  0`, which appears self-contradictory: it
looks like an amount equal to its limit, flagged with zero overage.

The detection is right; the **formatting** is wrong. Verified by calling the
calculation function directly, bypassing the display layer:

```python
>>> from main import check_individual_budget_warnings
>>> rec = {'transaction_id': 'TX996', 'transaction_type': 'Expense',
...        'category': 'Transport', 'description': 'Boundary over',
...        'amount_kes': 5000.01, 'budget_limit_kes': 5000.0,
...        'payment_method': 'Card'}
>>> check_individual_budget_warnings([rec])
[{'transaction_id': 'TX996', 'category': 'Transport', 'amount': 5000.01,
  'limit': 5000.0, 'over': 0.010000000000218279}]
```

The true overage is `0.01`. The cause is the format specifier in
`display_individual_warnings()`:

```python
print(f"{w['transaction_id']:<10} {w['category']:<15} {w['amount']:<12.0f} "
      f"{w['limit']:<12.0f} {w['over']:<12.0f}")
```

`.0f` rounds to **zero decimal places**. Since currency amounts have cents, any
overage below KES 1 displays as `0`.

**Recommended fix** — change the three numeric specifiers to `.2f`:

```python
print(f"{w['transaction_id']:<10} {w['category']:<15} {w['amount']:<12.2f} "
      f"{w['limit']:<12.2f} {w['over']:<12.2f}")
```

The same `.0f` issue affects `display_table()` and
`display_category_budget_summary()`.

*(The `0.010000000000218279` above is normal floating-point representation
error, not a program bug — 0.01 has no exact binary representation. `.2f`
formatting resolves it for display purposes.)*

---

## Test 6: Search Operation — Existing Transaction by ID

| Attribute | Value |
|-----------|-------|
| **Test ID** | T006 |
| **Category** | Search |
| **Objective** | Verify that searching by transaction ID returns the matching record |
| **Input** | Menu 2 → 2 (search), search term: `TX001` |
| **Expected Result** | TX001 found and displayed in the formatted table with all seven fields |
| **Actual Result** | As expected — single matching row displayed |
| **Status** | **PASS** |
| **Notes** | Search is case-insensitive; the term is lowercased before comparison, which is why the title reads `'tx001'` |

### Evidence

```
Enter selection: 2
1. Add a transaction
2. Search a transaction
Enter selection: 2

Search Transaction

Search by Transaction ID or Category: TX001

+--------------------------------------------------------------------------------------------------+
| Search Results for 'tx001'                                                                       |
+--------------------------------------------------------------------------------------------------+
| ID       | Type     | Category      | Description        | Amount     | Budget     | Payment     |
+--------------------------------------------------------------------------------------------------+
| TX001    | Expense  | Transport     | Fuel               | 1219       | 5500       | Card        |
+--------------------------------------------------------------------------------------------------+
```

---

## Test 7: Search Operation — Non-Existing Transaction

| Attribute | Value |
|-----------|-------|
| **Test ID** | T007 |
| **Category** | Search |
| **Objective** | Verify that searching for a non-existent record returns the appropriate message rather than an error |
| **Input** | Menu 2 → 2 (search), search term: `TX404` (not present in the dataset) |
| **Expected Result** | "No matching transactions found." displayed; program does not crash; menu repeats |
| **Actual Result** | As expected — message displayed, control returned to menu |
| **Status** | **PASS** |
| **Notes** | `TX404` was chosen deliberately because `TX999` is created by T001; reusing it would make this test order-dependent |

### Evidence

```
Enter selection: 2
1. Add a transaction
2. Search a transaction
Enter selection: 2

Search Transaction

Search by Transaction ID or Category: TX404
No matching transactions found.
```

---

## Test 8: Search Operation — Multiple Records by Category

| Attribute | Value |
|-----------|-------|
| **Test ID** | T008 |
| **Category** | Search |
| **Objective** | Verify that searching by category returns **all** matching transactions |
| **Input** | Menu 2 → 2 (search), search term: `Transport` |
| **Expected Result** | All valid Transport-category records returned in a single formatted table |
| **Actual Result** | As expected — 5 records returned (TX001, TX007, TX013, TX019, TRX2000) |
| **Status** | **PASS** |
| **Notes** | Matching is **exact and case-insensitive**, not substring — searching `Trans` returns no results |

### Evidence

```
Search by Transaction ID or Category: Transport

+--------------------------------------------------------------------------------------------------+
| Search Results for 'transport'                                                                   |
+--------------------------------------------------------------------------------------------------+
| ID       | Type     | Category      | Description        | Amount     | Budget     | Payment     |
+--------------------------------------------------------------------------------------------------+
| TX001    | Expense  | Transport     | Fuel               | 1219       | 5500       | Card        |
| TX007    | Expense  | Transport     | Fuel               | 5533       | 8000       | Bank        |
| TX013    | Expense  | Transport     | Fuel               | 9847       | 10500      | Card        |
| TX019    | Expense  | Transport     | Fuel               | 14161      | 13000      | Bank        |
| TRX2000  | Expense  | Transport     | Transportation     | 5000       | 6000       | Card        |
+--------------------------------------------------------------------------------------------------+
```

Sum check: 1219 + 5533 + 9847 + 14161 + 5000 = **35,760**, matching the
Transport figure in Test 13's category breakdown.

---

## Test 9: Menu Control — Invalid Menu Option

| Attribute | Value |
|-----------|-------|
| **Test ID** | T009 |
| **Category** | Menu |
| **Objective** | Verify that an out-of-range menu selection is rejected and the menu repeats |
| **Input** | At the main menu, enter `9` (valid options are 1–7) |
| **Expected Result** | "Invalid selection." displayed; menu redisplayed; program continues |
| **Actual Result** | As expected — error shown, loop continued, no crash |
| **Status** | **PASS** |
| **Notes** | Handled by the `else` branch of the `if`/`elif` chain, as required by the brief |

### Evidence

```
Enter selection: 9
Invalid selection.

=== Personal Expense and Budget Tracker ===
1. View valid transactions
2. Add or search a transaction
3. View income and expenditure summary
4. View budget warnings
5. View invalid records
6. View payment summary
7. Exit 

Enter selection: 7
Program closed.
```

---

## Test 10: Menu Control — Exit Option Terminates Program

| Attribute | Value |
|-----------|-------|
| **Test ID** | T010 |
| **Category** | Menu |
| **Objective** | Verify that option 7 terminates the program cleanly |
| **Input** | At the main menu, enter `7` |
| **Expected Result** | "Program closed." displayed; loop exits; process terminates with no error |
| **Actual Result** | As expected — message displayed and process exited cleanly |
| **Status** | **PASS** |
| **Notes** | `break` exits the `while True` loop; all added transactions were already written to CSV at add time |

### Evidence

```
=== Personal Expense and Budget Tracker ===
1. View valid transactions
2. Add or search a transaction
3. View income and expenditure summary
4. View budget warnings
5. View invalid records
6. View payment summary
7. Exit 

Enter selection: 7
Program closed.
```

---

## Test 11: Data Validation — Unrecognized Transaction Type

| Attribute | Value |
|-----------|-------|
| **Test ID** | T011 |
| **Category** | Invalid |
| **Objective** | Verify that an unrecognized transaction type is rejected rather than guessed at |
| **Input** | Existing CSV record TX011 (`transaction_type` = `EXP`), viewed via Menu option 5 |
| **Expected Result** | Rejected with reason `unrecognized transaction_type: 'EXP'` |
| **Actual Result** | As expected — listed with the correct reason, and the offending value quoted back |
| **Status** | **PASS** |
| **Notes** | Only `Income` and `Expense` are accepted. The brief permits standardizing alternatives **only where a mapping is defined**; no mapping is defined for `EXP`, so rejecting it is the correct behaviour |

### Evidence

```
Enter selection: 5
TX005 - amount must be greater than zero
TX011 - unrecognized transaction_type: 'EXP'
TX016 - missing category for expense
```

---

## Test 12: Data Validation — Non-Numeric Amount

| Attribute | Value |
|-----------|-------|
| **Test ID** | T012 |
| **Category** | Invalid |
| **Objective** | Verify that non-numeric input for amount is handled without crashing |
| **Input** | Menu 2 → 1 (add): ID: TX997, Type: Expense, Category: Food, Description: Snacks, Amount: `two thousand` |
| **Expected Result** | `ValueError` caught; "Invalid amount. Transaction not added." displayed; function returns early; menu repeats |
| **Actual Result** | As expected — error caught, message displayed, remaining prompts skipped, no traceback |
| **Status** | **PASS** |
| **Notes** | Note the function returns **immediately** — the Budget and Payment prompts never appear, confirming the early `return` |

### Evidence

```
--- Add new transaction ---


Transaction ID: TX997
Type (Income/Expense): Expense
Category: Food
Description: Snacks
Amount (KES): two thousand
Invalid amount. Transaction not added.

=== Personal Expense and Budget Tracker ===
```

**Code path exercised:** `try: amount = float(input(...))` raises `ValueError`
→ `except ValueError:` prints the message → `return` exits `add_transaction()`
before the budget prompt.

---

## Test 13: Summary Calculation — Correct Income/Expenditure Totals

| Attribute | Value |
|-----------|-------|
| **Test ID** | T013 |
| **Category** | Normal |
| **Objective** | Verify income, expenditure, balance and per-category totals are computed correctly from valid records only |
| **Input** | Menu option 3 on the unmodified dataset |
| **Expected Result** | Income = sum of Income records; Expenditure = sum of Expense records; Balance = Income − Expenditure; per-category breakdown of expenses |
| **Actual Result** | As expected — Income 27,384; Expenditure 114,098; Balance −86,714 (see arithmetic check) |
| **Status** | **PASS** |
| **Notes** | The three invalid records (TX005, TX011, TX016) are excluded, as intended |

### Evidence

```
Enter selection: 3


View Income and expenditure summary


****************************************
Total Income: 27384.0
Total Expenditure: 114098.0
Balance: -86714.0
----------------------------------------
Expenditure by category:
  Transport: 35760.0
  Housing: 33636.0
  Utilities: 20913.0
  Education: 11066.0
  Entertainment: 12723.0
****************************************
```

### Arithmetic verification

**Income** — the three valid Income records:

```
TX006  4,814
TX012  9,128
TX018 13,442
------------
      27,384   ✓ matches
```

**Category totals sum to total expenditure:**

```
Transport      35,760
Housing        33,636
Utilities      20,913
Education      11,066
Entertainment  12,723
---------------------
              114,098   ✓ matches Total Expenditure
```

**Balance:** 27,384 − 114,098 = **−86,714** ✓ matches

The negative balance is correct for this dataset — it contains 15 expenses
against 3 income records.

---

## Test 14: Budget Warnings — Individual and Category Levels

| Attribute | Value |
|-----------|-------|
| **Test ID** | T014 |
| **Category** | Normal |
| **Objective** | Verify warnings are produced at both the individual-transaction and category-aggregate levels |
| **Input** | Menu option 4 on the unmodified dataset |
| **Expected Result** | Individual table lists expenses exceeding their own limit; category table lists categories whose total spend exceeds their total budget |
| **Actual Result** | As expected — 5 individual warnings and 1 category warning (see evidence and spot-check) |
| **Status** | **PASS** |
| **Notes** | Two independent checks. The brief requires the category-level warning; the individual-level check is additional |

### Evidence

```
Enter selection: 4

================================================================================
INDIVIDUAL TRANSACTION WARNINGS
================================================================================
ID         Category        Amount       Limit        Over by     
--------------------------------------------------------------------------------
TX010      Education       7690         3000         4690        
TX015      Utilities       11285        3000         8285        
TX017      Entertainment   12723        8000         4723        
TX019      Transport       14161        13000        1161        
TX020      Housing         14880        3000         11880       
================================================================================


================================================================================
CATEGORY BUDGET SUMMARY
================================================================================
Category        Spent        Budget       Over by     
--------------------------------------------------------------------------------
Entertainment   12723        8000         4723        
================================================================================
```

### Spot-check of the logic

**Individual level** — TX020: amount 14,880 against its own limit of 3,000.
Over by 14,880 − 3,000 = **11,880** ✓ matches the printed row.

**Category level** — Entertainment has one valid expense (TX017: 12,723,
limit 8,000). TX011 is in the same category but invalid, so it is excluded.
Spent 12,723 > budget 8,000, over by **4,723** ✓ matches.

**Why only Entertainment appears at category level:** each category sums the
budget limits of *all* its records, so multi-record categories accumulate a
large combined allowance. Transport, for example, totals 35,760 spent against
5,500 + 8,000 + 10,500 + 13,000 + 6,000 = 43,000 budget — under, despite TX019
individually breaching its own limit. This is why both levels are needed:
neither alone gives the full picture.

---

## Test Summary

| Test ID | Category | Description | Status |
|---------|----------|-------------|--------|
| T001 | Normal | Valid transaction accepted and persisted | PASS |
| T002 | Invalid | Missing category rejected | PASS |
| T003 | Invalid | Negative amount rejected | PASS |
| T004 | Boundary | Amount = budget limit (no warning) | PASS |
| T005 | Boundary | Amount just over limit (warning raised) | PASS — defect found in display |
| T006 | Search | Search by existing ID | PASS |
| T007 | Search | Search for non-existent record | PASS |
| T008 | Search | Search by category (multiple results) | PASS |
| T009 | Menu | Invalid menu option rejected | PASS |
| T010 | Menu | Exit option terminates program | PASS |
| T011 | Invalid | Unrecognized transaction type | PASS |
| T012 | Invalid | Non-numeric amount at add time | PASS |
| T013 | Normal | Summary calculations correct | PASS |
| T014 | Normal | Budget warnings at both levels | PASS |

**Total tests:** 14
**Passed:** 14
**Failed:** 0
**Defects found:** 1 (display formatting — T005)

---

## Defects and Observations

### D1 — Overage under KES 1 displays as `0` (from T005)

Detection is correct; display rounds to whole units. Change the `.0f` format
specifiers to `.2f` in `display_individual_warnings()`,
`display_category_budget_summary()` and `display_table()`.

**Severity:** Low — cosmetic, but misleading on a warnings report.

### D2 — `highest_spending_category()` is never called

The function is implemented and correct, but no menu option invokes it. The
brief lists "Identify the highest-spending category" as a required task.

Verified by direct call:

```python
>>> from main import load_transactions, validate_all, highest_spending_category
>>> valid, invalid = validate_all(load_transactions())
>>> highest_spending_category(valid)
('Transport', 35760.0)
```

**Suggested fix** — append to `display_summary()`:

```python
category, amount = highest_spending_category(valid_records)
print(f"Highest spending category: {category} ({amount})")
```

**Severity:** Medium — a required feature is unreachable from the user interface.

### D3 — `TRX2000` is not part of the source dataset

`cap-data.csv` contains a 21st record, `TRX2000`, which does not appear in the
`09_Expense_Tracker` worksheet. It appears to be test data left behind by the
add-transaction feature and committed. It is included in all totals above.

**Severity:** Low — but it should be removed before final submission so results
are reproducible from the supplied dataset.

---

## Test Execution Notes

- All tests were executed against `main.py` with `cap-data.csv` as supplied,
  restored to its original state between tests.
- Invalid records (T003, T011, and TX016) are detected at **load** time by
  `validate_all()`; T002 and T012 are detected at **add** time. Both paths call
  the same `validate_transaction()` function.
- No test produced an unhandled exception or traceback.
- Menu control (T009, T010) confirms the loop is robust and exits cleanly.
- Search (T006–T008) handles zero, one and many results.
- Boundary tests (T004–T005) confirm the comparison is strict `>`, not `>=`.
- T007 uses `TX404` rather than `TX999` so the suite is order-independent —
  T001 creates `TX999`, which would otherwise cause T007 to fail when the tests
  are run in sequence.
