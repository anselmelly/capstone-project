#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 14:42:25 2026

Group Members
Lewis Munyi
Ansel Melly
Ruth Kwamboka
Ivy Managene
Josiah Wandera
"""


# ----- FUNCTIONS -----

import csv

def load_transactions():
    """Loads the transaction dataset with proper type casting."""
    with open('cap-data.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            
            # Cast numeric fields
            row["amount_kes"] = float(row["amount_kes"])
            row["budget_limit_kes"] = float(row["budget_limit_kes"])
            
            # Strip whitespace from all string values
            for key in row:
                if isinstance(row[key], str):
                    row[key] = row[key].strip()
            
            data.append(row)
    return data

def validate_transaction(record):
    reasons = []

    # Validate transaction_type
    tx_type = record.get("transaction_type", "").strip()
    if tx_type not in ("Income", "Expense"):
        reasons.append(f"unrecognized transaction_type: '{tx_type}'")

    # Validate amount_kes
    try:
        amount = float(record.get("amount_kes", 0))
        if amount <= 0:
            reasons.append("amount must be greater than zero")
    except (ValueError, TypeError):
        reasons.append("amount must be numeric")

    # Category required for Expenses
    category = record.get("category", "").strip()
    if tx_type.lower() == "expense" and not category:
        reasons.append("missing category for expense")

    # Validate budget_limit_kes
    try:
        budget = float(record.get("budget_limit_kes", 0))
        if budget < 0:
            reasons.append("negative budget limit")
    except (ValueError, TypeError):
        reasons.append("budget_limit_kes must be numeric")

    return reasons

def validate_all(transactions):
    valid_records = []
    invalid_records = []

    for record in transactions:
        reasons = validate_transaction(record)
        
        if reasons:
            invalid_records.append({"record": record, "reasons": reasons})
        else:
            valid_records.append(record)

    return valid_records, invalid_records

def add_transaction(transactions):
    print("\n\n--- Add new transaction ---\n\n")
    transaction_id = input("Transaction ID: ").strip()
    transaction_type = input("Type (Income/Expense): ").strip()
    category = input("Category: ").strip()
    description = input("Description: ").strip()

    try:
        amount = float(input("Amount (KES): "))
    except ValueError:
        print("Invalid amount. Transaction not added.")
        return
    try:
        budget_limit = float(input("Budget limit (KES): "))
    except ValueError:
        print("Invalid budget limit. Transaction not added.")
        return


    payment_method = input("Payment method: ").strip()

    new_record = {
        "transaction_id": transaction_id,
        "transaction_type": transaction_type,
        "category": category,
        "description": description,
        "amount_kes": amount,
        "budget_limit_kes": budget_limit,
        "payment_method": payment_method
    }

    reasons = validate_transaction(new_record)
    if reasons:
        print("Transaction rejected:")
        for r in reasons:
            print(" -", r)
    else:
        transactions.append(new_record)

        write_transactions(transactions)
        
        print("Transaction added successfully.")

def write_transactions(transactions, filename='cap-data.csv'):
    """Write all transactions back to CSV file."""
    if not transactions:
        print("No transactions to write.")
        return

    fieldnames = [
        "transaction_id",
        "transaction_type",
        "category",
        "description",
        "amount_kes",
        "budget_limit_kes",
        "payment_method"
    ]

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)

def search_transaction(valid_records):
    print("\nSearch Transaction\n")
    term = input("Search by Transaction ID or Category: ").strip().lower()
    matches = []
    for r in valid_records:
        if term == r["transaction_id"].lower() or term == r["category"].lower():
            matches.append(r)

    if not matches:
        print("No matching transactions found.")
    else:
        display_table(matches, f"Search Results for '{term}'")


def add_or_search_transaction(transactions, valid_records):
    print("1. Add a transaction")
    print("2. Search a transaction")
    sub_choice = input("Enter selection: ").strip()

    if sub_choice == "1":
        add_transaction(transactions)
    elif sub_choice == "2":
        search_transaction(valid_records)
    else:
        print("Invalid selection.")

def calculate_summary(valid_records):
    total_income = 0
    total_expenditure = 0
    category_totals = {}

    for record in valid_records:
        amount = record["amount_kes"]
        if record["transaction_type"] == "Income":
            total_income = total_income + amount
        else:
            total_expenditure = total_expenditure + amount
            category = record["category"]
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] = category_totals[category] + amount

    balance = total_income - total_expenditure
    return total_income, total_expenditure, balance, category_totals


def display_summary(valid_records):
    
    print("\n\nView Income and expenditure summary\n\n")
    
    total_income, total_expenditure, balance, category_totals = calculate_summary(valid_records)

    print("*" * 40)
    print("Total Income:", total_income)
    print("Total Expenditure:", total_expenditure)
    print("Balance:", balance)
    print("-" * 40)
    print("Expenditure by category:")
    for category, total in category_totals.items():
        print(f"  {category}: {total}")
    print("*" * 40)


def check_individual_budget_warnings(valid_records):
    """Check if individual transactions exceed their own budget limits."""
    warnings = []
    for record in valid_records:
        if record["transaction_type"] == "Expense":
            if record["amount_kes"] > record["budget_limit_kes"]:
                warnings.append({
                    "transaction_id": record["transaction_id"],
                    "category": record["category"],
                    "amount": record["amount_kes"],
                    "limit": record["budget_limit_kes"],
                    "over": record["amount_kes"] - record["budget_limit_kes"]
                })
    return warnings


def display_individual_warnings(valid_records):
    """Display individual transactions over budget."""
    warnings = check_individual_budget_warnings(valid_records)
    
    if not warnings:
        print("All individual transactions are within budget.")
    else:
        print("\n" + "=" * 80)
        print("INDIVIDUAL TRANSACTION WARNINGS")
        print("=" * 80)
        print(f"{'ID':<10} {'Category':<15} {'Amount':<12} {'Limit':<12} {'Over by':<12}")
        print("-" * 80)
        for w in warnings:
            print(f"{w['transaction_id']:<10} {w['category']:<15} {w['amount']:<12.0f} {w['limit']:<12.0f} {w['over']:<12.0f}")
        print("=" * 80 + "\n")


def check_category_budget_summary(valid_records):
    """Check category totals vs. sum of budget limits per category."""
    category_totals = {}
    category_budgets = {}
    
    for record in valid_records:
        if record["transaction_type"] == "Expense":
            cat = record["category"]
            if cat not in category_totals:
                category_totals[cat] = 0
                category_budgets[cat] = 0
            category_totals[cat] += record["amount_kes"]
            category_budgets[cat] += record["budget_limit_kes"]
    
    warnings = []
    for category, spent in category_totals.items():
        limit = category_budgets[category]
        if spent > limit:
            warnings.append({
                "category": category,
                "spent": spent,
                "budget": limit,
                "over": spent - limit
            })
    
    return warnings


def display_category_budget_summary(valid_records):
    """Display category-level budget summary."""
    warnings = check_category_budget_summary(valid_records)
    
    if not warnings:
        print("All categories are within budget.")
    else:
        print("\n" + "=" * 80)
        print("CATEGORY BUDGET SUMMARY")
        print("=" * 80)
        print(f"{'Category':<15} {'Spent':<12} {'Budget':<12} {'Over by':<12}")
        print("-" * 80)
        for w in warnings:
            print(f"{w['category']:<15} {w['spent']:<12.0f} {w['budget']:<12.0f} {w['over']:<12.0f}")
        print("=" * 80 + "\n")


def display_all_budget_warnings(valid_records):
    """Display both individual and category-level warnings."""
    display_individual_warnings(valid_records)
    display_category_budget_summary(valid_records)


def highest_spending_category(valid_records):
    _, _, _, category_totals = calculate_summary(valid_records)
    if not category_totals:
        return None, 0

    highest_category = None
    highest_amount = None
    for category, total in category_totals.items():
        if highest_amount is None or total > highest_amount:
            highest_amount = total
            highest_category = category

    return highest_category, highest_amount


def count_payment_methods(valid_records):
    counts = {}
    for record in valid_records:
        method = record["payment_method"]
        if method not in counts:
            counts[method] = 0
        counts[method] = counts[method] + 1
    return counts


def display_payment_summary(valid_records):
    counts = count_payment_methods(valid_records)
    print("*" * 40)
    print("Transactions by payment method:")
    for method, count in counts.items():
        print(f"  {method}: {count}")
    print("*" * 40)
    
def display_table(records, title="Transactions"):
    """Display records in a formatted ASCII table."""
    if not records:
        print("No records to display.")
        return

    print("\n" + "+" + "-" * 98 + "+")
    print(f"| {title:<96} |")
    print("+" + "-" * 98 + "+")
    print(f"| {'ID':<8} | {'Type':<8} | {'Category':<13} | {'Description':<18} | {'Amount':<10} | {'Budget':<10} | {'Payment':<11} |")
    print("+" + "-" * 98 + "+")
    
    for r in records:
        print(f"| {r['transaction_id']:<8} | {r['transaction_type']:<8} | {r['category']:<13} | {r['description']:<18} | {r['amount_kes']:<10.0f} | {r['budget_limit_kes']:<10.0f} | {r['payment_method']:<11} |")
    
    print("+" + "-" * 98 + "+\n")

def view_transactions(valid_records):
    display_table(valid_records, "All Valid Transactions")
    
def main():
    transactions = load_transactions()
    valid_records, invalid_records = validate_all(transactions)
    
    while True:
        # ---------- Menu ----------
        print("\n=== Personal Expense and Budget Tracker ===")
        print("1. View valid transactions")
        print("2. Add or search a transaction")
        print("3. View income and expenditure summary")
        print("4. View budget warnings")
        print("5. View invalid records")
        print("6. View payment summary")
        print("7. Exit \n\n\n")
    
        choice = input("Enter selection: ").strip()
    
        if choice == "1":
            view_transactions(valid_records)
    
        elif choice == "2":
            add_or_search_transaction(transactions, valid_records)
            valid_records, invalid_records = validate_all(transactions)
    
        elif choice == "3":
            display_summary(valid_records)
    
        elif choice == "4":
            display_all_budget_warnings(valid_records)
    
        elif choice == "5":
            for entry in invalid_records:
                print(entry["record"]["transaction_id"], "-", ", ".join(entry["reasons"]))
    
        elif choice == "6":
            display_payment_summary(valid_records)
    
        elif choice == "7":
            print("Program closed.")
            break
    
        else:
            print("Invalid selection.")    

if __name__ == "__main__":
    main()