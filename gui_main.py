#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Expense and Budget Tracker — GUI version

This file adds a Tkinter interface on top of the existing program logic.
It does NOT reimplement any validation or calculation rules — it imports
them directly from main.py, so both the CLI (main.py) and this GUI stay
in sync and are tested against the same functions.

Run from the same folder as main.py and cap-data.csv:
    python3 gui_main.py

Menu -> GUI mapping (same 7 operations from the brief):
    1. View valid transactions      -> "Valid Transactions" tab
    2. Add or search a transaction  -> "Add / Search" tab
    3. Income & expenditure summary -> "Summary" tab
    4. Budget warnings               -> "Budget Warnings" tab
    5. Invalid records                -> "Invalid Records" tab
    6. Payment summary                -> "Payment Summary" tab
    7. Exit                           -> Exit button / closing the window
"""

import tkinter as tk
from tkinter import ttk, messagebox

from main import (
    load_transactions,
    validate_all,
    validate_transaction,
    write_transactions,
    calculate_summary,
    highest_spending_category,
    check_individual_budget_warnings,
    check_category_budget_summary,
    calculate_payment_method_totals,
)

COLUMNS = ("transaction_id", "transaction_type", "category", "description",
           "amount_kes", "budget_limit_kes", "payment_method")
HEADERS = ("ID", "Type", "Category", "Description", "Amount (KES)",
           "Budget (KES)", "Payment")


class BudgetTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Expense and Budget Tracker")
        self.geometry("980x600")

        # ---- Load data (same as main() in main.py) ----
        self.transactions = load_transactions()
        self.valid_records, self.invalid_records = validate_all(self.transactions)

        # ---- Layout ----
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.tab_valid = ttk.Frame(notebook)
        self.tab_add_search = ttk.Frame(notebook)
        self.tab_summary = ttk.Frame(notebook)
        self.tab_warnings = ttk.Frame(notebook)
        self.tab_invalid = ttk.Frame(notebook)
        self.tab_payment = ttk.Frame(notebook)

        notebook.add(self.tab_valid, text="1. Valid Transactions")
        notebook.add(self.tab_add_search, text="2. Add / Search")
        notebook.add(self.tab_summary, text="3. Summary")
        notebook.add(self.tab_warnings, text="4. Budget Warnings")
        notebook.add(self.tab_invalid, text="5. Invalid Records")
        notebook.add(self.tab_payment, text="6. Payment Summary")

        self.notebook = notebook

        self._build_valid_tab()
        self._build_add_search_tab()
        self._build_summary_tab()
        self._build_warnings_tab()
        self._build_invalid_tab()
        self._build_payment_tab()

        # Bottom bar with Exit (menu option 7) and a manual Refresh
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Button(bottom, text="Refresh all tabs", command=self.refresh_all).pack(side="left")
        ttk.Button(bottom, text="7. Exit", command=self.destroy).pack(side="right")

        self.refresh_all()

    # ---------------------------------------------------------------
    # Small helper to build a Treeview table used by several tabs
    # ---------------------------------------------------------------
    def _make_table(self, parent, columns, headers, widths=None):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        for col, head in zip(columns, headers):
            tree.heading(col, text=head)
            tree.column(col, width=(widths.get(col, 100) if widths else 100), anchor="w")
        vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        return tree

    def _fill_table(self, tree, rows):
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=row)

    # ---------------------------------------------------------------
    # Tab 1: View valid transactions
    # ---------------------------------------------------------------
    def _build_valid_tab(self):
        frame = ttk.Frame(self.tab_valid)
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        widths = {"transaction_id": 70, "description": 160}
        self.valid_tree = self._make_table(frame, COLUMNS, HEADERS, widths)

    def refresh_valid_tab(self):
        rows = [tuple(r[c] if c not in ("amount_kes", "budget_limit_kes")
                       else f"{r[c]:.2f}" for c in COLUMNS) for r in self.valid_records]
        self._fill_table(self.valid_tree, rows)

    # ---------------------------------------------------------------
    # Tab 2: Add / Search
    # ---------------------------------------------------------------
    def _build_add_search_tab(self):
        outer = ttk.Frame(self.tab_add_search)
        outer.pack(fill="both", expand=True, padx=8, pady=8)

        # --- Add transaction form ---
        add_frame = ttk.LabelFrame(outer, text="Add a transaction")
        add_frame.pack(side="top", fill="x", pady=(0, 10))

        labels = ["Transaction ID", "Type (Income/Expense)", "Category",
                  "Description", "Amount (KES)", "Budget limit (KES)", "Payment method"]
        self.add_entries = {}
        for i, label in enumerate(labels):
            ttk.Label(add_frame, text=label + ":").grid(row=i // 2, column=(i % 2) * 2,
                                                          sticky="w", padx=5, pady=4)
            entry = ttk.Entry(add_frame, width=25)
            entry.grid(row=i // 2, column=(i % 2) * 2 + 1, sticky="w", padx=5, pady=4)
            self.add_entries[label] = entry

        ttk.Button(add_frame, text="Add transaction", command=self.on_add_transaction).grid(
            row=4, column=0, columnspan=4, pady=8)

        # --- Search ---
        search_frame = ttk.LabelFrame(outer, text="Search by Transaction ID or Category")
        search_frame.pack(side="top", fill="x", pady=(0, 10))
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5, pady=6)
        ttk.Button(search_frame, text="Search", command=self.on_search).pack(side="left", padx=5)

        results_frame = ttk.LabelFrame(outer, text="Results")
        results_frame.pack(fill="both", expand=True)
        widths = {"transaction_id": 70, "description": 160}
        self.search_tree = self._make_table(results_frame, COLUMNS, HEADERS, widths)

    def on_add_transaction(self):
        e = self.add_entries
        try:
            amount = float(e["Amount (KES)"].get())
        except ValueError:
            messagebox.showerror("Invalid amount", "Amount must be numeric. Transaction not added.")
            return
        try:
            budget_limit = float(e["Budget limit (KES)"].get())
        except ValueError:
            messagebox.showerror("Invalid budget limit", "Budget limit must be numeric. Transaction not added.")
            return

        new_record = {
            "transaction_id": e["Transaction ID"].get().strip(),
            "transaction_type": e["Type (Income/Expense)"].get().strip(),
            "category": e["Category"].get().strip(),
            "description": e["Description"].get().strip(),
            "amount_kes": amount,
            "budget_limit_kes": budget_limit,
            "payment_method": e["Payment method"].get().strip(),
        }

        reasons = validate_transaction(new_record)
        if reasons:
            messagebox.showerror("Transaction rejected", "Reasons:\n\n- " + "\n- ".join(reasons))
            return

        self.transactions.append(new_record)
        write_transactions(self.transactions)
        for entry in e.values():
            entry.delete(0, tk.END)
        messagebox.showinfo("Success", f"Transaction {new_record['transaction_id']} added successfully.")
        self.refresh_all()

    def on_search(self):
        term = self.search_entry.get().strip().lower()
        matches = [r for r in self.valid_records
                   if term == r["transaction_id"].lower() or term == r["category"].lower()]
        rows = [tuple(r[c] if c not in ("amount_kes", "budget_limit_kes")
                       else f"{r[c]:.2f}" for c in COLUMNS) for r in matches]
        self._fill_table(self.search_tree, rows)
        if not matches:
            messagebox.showinfo("No results", "No matching transactions found.")

    # ---------------------------------------------------------------
    # Tab 3: Summary
    # ---------------------------------------------------------------
    def _build_summary_tab(self):
        self.summary_text = tk.Text(self.tab_summary, wrap="none", font=("Courier New", 10))
        self.summary_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.summary_text.configure(state="disabled")

    def refresh_summary_tab(self):
        income, expenditure, balance, category_totals = calculate_summary(self.valid_records)
        category, amount = highest_spending_category(self.valid_records)

        lines = []
        lines.append("INCOME AND EXPENDITURE SUMMARY")
        lines.append("=" * 50)
        lines.append(f"{'Total Income':<25} KES {income:>15.2f}")
        lines.append(f"{'Total Expenditure':<25} KES {expenditure:>15.2f}")
        lines.append(f"{'Balance':<25} KES {balance:>15.2f}")
        lines.append("")
        lines.append("EXPENDITURE BY CATEGORY")
        lines.append("-" * 50)
        for cat, total in category_totals.items():
            lines.append(f"{cat:<25} KES {total:>15.2f}")
        if category is not None:
            lines.append("")
            lines.append(f"Highest spending category: {category} (KES {amount:.2f})")

        self._set_text(self.summary_text, "\n".join(lines))

    def _set_text(self, widget, content):
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, content)
        widget.configure(state="disabled")

    # ---------------------------------------------------------------
    # Tab 4: Budget warnings
    # ---------------------------------------------------------------
    def _build_warnings_tab(self):
        top = ttk.LabelFrame(self.tab_warnings, text="Individual transaction warnings")
        top.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        ind_cols = ("transaction_id", "category", "amount", "limit", "over")
        ind_headers = ("ID", "Category", "Amount", "Limit", "Over by")
        self.ind_warn_tree = self._make_table(top, ind_cols, ind_headers)

        bottom = ttk.LabelFrame(self.tab_warnings, text="Category budget summary")
        bottom.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        cat_cols = ("category", "spent", "budget", "status")
        cat_headers = ("Category", "Spent", "Budget", "Status")
        self.cat_warn_tree = self._make_table(bottom, cat_cols, cat_headers)

    def refresh_warnings_tab(self):
        warnings = check_individual_budget_warnings(self.valid_records)
        rows = [(w["transaction_id"], w["category"], f"{w['amount']:.2f}",
                 f"{w['limit']:.2f}", f"{w['over']:.2f}") for w in warnings]
        self._fill_table(self.ind_warn_tree, rows)

        summary = check_category_budget_summary(self.valid_records)
        rows = [(s["category"], f"{s['spent']:.2f}", f"{s['budget']:.2f}", s["status"])
                for s in summary]
        self._fill_table(self.cat_warn_tree, rows)

    # ---------------------------------------------------------------
    # Tab 5: Invalid records
    # ---------------------------------------------------------------
    def _build_invalid_tab(self):
        frame = ttk.Frame(self.tab_invalid)
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        cols = ("transaction_id", "transaction_type", "category", "description", "amount_kes", "reasons")
        headers = ("ID", "Type", "Category", "Description", "Amount", "Reasons")
        widths = {"reasons": 300, "description": 160}
        self.invalid_tree = self._make_table(frame, cols, headers, widths)

    def refresh_invalid_tab(self):
        rows = []
        for entry in self.invalid_records:
            r = entry["record"]
            reasons = ", ".join(entry["reasons"])
            rows.append((r["transaction_id"], r["transaction_type"], r["category"],
                         r["description"], r["amount_kes"], reasons))
        self._fill_table(self.invalid_tree, rows)

    # ---------------------------------------------------------------
    # Tab 6: Payment summary
    # ---------------------------------------------------------------
    def _build_payment_tab(self):
        frame = ttk.Frame(self.tab_payment)
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        cols = ("method", "count", "amount", "budget")
        headers = ("Method", "Count", "Total Amount", "Total Budget")
        self.payment_tree = self._make_table(frame, cols, headers)

    def refresh_payment_tab(self):
        method_data = calculate_payment_method_totals(self.valid_records)
        rows = [(method, data["count"], f"{data['amount']:.2f}", f"{data['budget']:.2f}")
                for method, data in method_data.items()]
        self._fill_table(self.payment_tree, rows)

    # ---------------------------------------------------------------
    def refresh_all(self):
        self.valid_records, self.invalid_records = validate_all(self.transactions)
        self.refresh_valid_tab()
        self.refresh_summary_tab()
        self.refresh_warnings_tab()
        self.refresh_invalid_tab()
        self.refresh_payment_tab()


if __name__ == "__main__":
    app = BudgetTrackerApp()
    app.mainloop()
