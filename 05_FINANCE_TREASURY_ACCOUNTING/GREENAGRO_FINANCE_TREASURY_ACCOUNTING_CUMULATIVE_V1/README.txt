GREENAGRO MODULE 05 — FINANCE, TREASURY & ACCOUNTING — CUMULATIVE V1

Forms:
01 Chart of Accounts & Financial Masters
02 Supplier Invoice & Accounts Payable
03 Customer Invoice & Accounts Receivable
04 Treasury Cash/Bank Receipts & Payments
05 OPEX/CAPEX & Journal Adjustment Control
06 Read-only Finance Management Reporting & Audit Engine

Architecture:
Procure-to-pay: PO -> receipt/acceptance -> AP -> Treasury payment.
Order-to-cash: Sales order -> delivery/POD -> AR -> Treasury receipt.
Cash & Bank Book is derived from Treasury transactions, never re-entered.
AR/AP outstanding is derived from invoices minus linked posted Treasury movements.

Final GEMS integration must replace localStorage/free-text identities with central database, authenticated employees, role/duty permissions, immutable audit events, server-side approval workflow, locked accounting periods, automatic numbering, source-document validation, and controlled reversal rather than deletion.
