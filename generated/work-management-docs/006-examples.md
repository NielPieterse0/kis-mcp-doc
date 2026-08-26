<!-- GENERATED — DO NOT EDIT -->
# Work Management examples

These examples compose canonical operations and states; they do not create new transitions or authority.

## Example: take and complete ready work

1. Confirm the item satisfies Ready metadata and dependency requirements.
2. Use `take_next_work` or `claim_work` to establish the execution claim.
3. Perform the governed repository change while Work remains evidence-linked to its delivery stage.
4. Run source verification for the exact delivery identity.
5. After merge, complete required documentation reconciliation and any required commissioning.
6. Use `complete_work` only after the completion guards are satisfied.

If a guard rejects a transition, resolve its reason code instead of forcing the state.

For exact transitions, guards, fields, and operation contracts, use the [Work Management Specification](../work-management-spec/001-specification.md).
