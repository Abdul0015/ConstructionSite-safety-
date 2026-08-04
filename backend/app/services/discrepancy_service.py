from typing import Optional, List, Tuple

def evaluate_delivery_discrepancy(
    ai_vehicle_count: Optional[int],
    manual_reported_count: int,
    recent_gate_discrepancy_flags: Optional[List[bool]] = None
) -> Tuple[bool, bool]:
    """
    Evaluates delivery count discrepancy and determines escalation status.
    
    Args:
        ai_vehicle_count: AI detected vehicle count at the gate (None if no AI count exists yet).
        manual_reported_count: Supervisor manually reported delivery vehicle count.
        recent_gate_discrepancy_flags: List of recent discrepancy_flag booleans for this gate (ordered newest to oldest).
        
    Returns:
        Tuple[bool, bool]: (discrepancy_flag, is_escalated)
        - discrepancy_flag: True if count mismatch exists, False if counts match or AI count is unavailable.
        - is_escalated: True ONLY if 3 consecutive mismatches have occurred at this gate.
    """
    # Edge case: If delivery log is submitted before any AI vehicle count exists, do NOT falsely flag as discrepancy.
    if ai_vehicle_count is None:
        return False, False

    # Check for count mismatch
    is_mismatch = (ai_vehicle_count != manual_reported_count)

    if not is_mismatch:
        return False, False

    # Discrepancy detected (single mismatch)
    discrepancy_flag = True

    # Escalation check: Requires 3 consecutive mismatches at the same gate
    # Check if the previous 2 recent logs were also mismatches (discrepancy_flag == True)
    if recent_gate_discrepancy_flags and len(recent_gate_discrepancy_flags) >= 2:
        # Check if preceding 2 logs are True
        preceding_two = recent_gate_discrepancy_flags[:2]
        if all(flag is True for flag in preceding_two):
            return discrepancy_flag, True

    return discrepancy_flag, False
