# FCC CAPSTONE PROJECT – ALGORITHM SUMMARY

### 1. Store the transaction records
- Load the records from `cap-data.csv` using Python's built-in `csv` module.
- Store the records as a list of dictionaries.
- Convert the amount and budget-limit fields to numeric values.

### 2. Define a function to validate transactions
- Check that the transaction type is `Income` or `Expense`.
- Check that the amount is numeric and greater than zero.
- Check that the category is provided for `Expense` transactions.
- Check that the budget limit is not negative.

### 3. Define a function to view transactions
- Display valid or invalid transactions according to the user's selection.

### 4. Define a function to add a transaction
- Ask the user to enter the transaction details.
- Validate the amount and budget limit.
- Add the new transaction to the transaction list.

### 5. Define a function to search for a transaction
- Ask the user for a transaction ID or category.
- Search the transaction list.
- Display the matching transaction or indicate that it was not found.

### 6. Define a function to calculate the income and expenditure summary
- Calculate total income.
- Calculate total expenditure.
- Calculate the balance.
- Calculate category totals.
- Identify the highest-spending category.

### 7. Define a function to identify budget warnings
- Compare each transaction's amount with its own budget limit and flag it when exceeded.
- Calculate expenditure by category.
- Compare category expenditure with the relevant budget.
- Display a warning when expenditure exceeds the budget.

### 8. Define a function to display invalid transactions
- Check each transaction using the validation function.
- Display transactions that fail validation.

### 9. Define a function to display the payment summary
- Count transactions according to payment method.
- Display the totals.

### 10. Define a function to exit the program

### 11. Ask the user to select an operation
- If the selection is invalid, display an error message and return to the menu.

### 12. Call the function corresponding to the selected operation
- Each non-exit menu option calls its appropriate function.

### 13. Repeat the menu and operation selection until the user selects Exit

### 14. Display a closing message

**END**