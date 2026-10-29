# StackTrace: PL/SQL PDA Visualizer

Open `index.html` in a modern browser. Load a local `.sql`, `.pls`, or `.pl` file with **Open SQL / PL file**.

The main visual is a code-specific PDA trace diagram. Use **Next step**, **Back**, or **Play** to follow each recognized opener and closer. Every step shows the source line, PUSH/POP or rejection action, and the stack contents after that action. You can also select a trace row to jump directly to that step. The colors follow the Vanilla Cream, Cherry Velvet, and Sky Powder theme.

Both demo files contain three intentional wrong-order closers. Analyze either, then use **Apply all fixes** to plan and apply the repairs together.

- `examples/demo_order_review.sql` — order processing scenario.
- `examples/demo_account_review.pl` — account review scenario.

After a completed, balanced analysis, **Download Corrected SQL** appears at the bottom. It saves a separate copy and preserves the loaded file extension, including `.pl`. This tool checks block nesting only; it does not execute or fully compile PL/SQL.
